"""
MCP Server for Recommender Systems - Collaborative Filtering
"""

from typing import Any, List, Dict
import pandas as pd
import numpy as np
from pathlib import Path
from mcp.server.fastmcp import FastMCP
import logging

# Initialize FastMCP server
mcp = FastMCP("recommender-systems")

# Setup logging to stderr (NOT stdout - as per MCP guidelines)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]  # Writes to stderr by default
)
logger = logging.getLogger(__name__)

# Global variables for data storage
ratings_df: pd.DataFrame = None
DATA_PATH = Path(__file__).parent.parent / "data" / "ratings.csv"


def load_or_initialize_data():
    """Load ratings data or initialize with sample data."""
    global ratings_df
    
    try:
        if DATA_PATH.exists():
            ratings_df = pd.read_csv(DATA_PATH)
            logger.info(f"Loaded {len(ratings_df)} ratings from {DATA_PATH}")
        else:
            # Initialize with sample data
            logger.info("Creating sample data...")
            sample_data = {
                'user_id': [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5],
                'item_id': [101, 102, 103, 101, 102, 104, 102, 103, 104, 101, 103, 105, 102, 104, 105],
                'rating': [5.0, 3.0, 4.0, 4.0, 2.0, 5.0, 3.0, 5.0, 4.0, 5.0, 4.0, 3.0, 2.0, 5.0, 4.0]
            }
            ratings_df = pd.DataFrame(sample_data)
            
            # Save sample data
            DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
            ratings_df.to_csv(DATA_PATH, index=False)
            logger.info(f"Saved sample data to {DATA_PATH}")
            
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise


def calculate_user_similarity(user1_ratings: pd.Series, user2_ratings: pd.Series) -> float:
    """
    Calculate cosine similarity between two users based on common rated items.
    
    Args:
        user1_ratings: Ratings of user 1
        user2_ratings: Ratings of user 2
    
    Returns:
        Similarity score between 0 and 1
    """
    # Find common items (must be rated by both users - not NaN)
    common_items = user1_ratings.index.intersection(user2_ratings.index)
    common_items = [item for item in common_items 
                    if pd.notna(user1_ratings[item]) and pd.notna(user2_ratings[item])]
    
    if len(common_items) == 0:
        return 0.0
    
    # Get ratings for common items
    r1 = user1_ratings[common_items].values
    r2 = user2_ratings[common_items].values
    
    # Calculate cosine similarity
    dot_product = np.dot(r1, r2)
    norm1 = np.linalg.norm(r1)
    norm2 = np.linalg.norm(r2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))


@mcp.tool()
async def get_recommendations(user_id: int, top_n: int = 5) -> str:
    """
    Get top N item recommendations for a user using collaborative filtering.
    Uses user-based collaborative filtering with cosine similarity.
    
    Args:
        user_id: ID of the user to get recommendations for
        top_n: Number of recommendations to return (default: 5)
    
    Returns:
        JSON string with recommended items and predicted ratings
    """
    try:
        if ratings_df is None:
            return "Error: Data not loaded. Please initialize the system first."
        
        # Get target user's ratings
        user_ratings = ratings_df[ratings_df['user_id'] == user_id]
        
        if len(user_ratings) == 0:
            return f"Error: User {user_id} not found in the system."
        
        # Get all items rated by target user
        rated_items = set(user_ratings['item_id'].values)
        
        # Create user-item matrix for similarity calculation
        user_item_matrix = ratings_df.pivot_table(
            index='user_id', 
            columns='item_id', 
            values='rating'
        )
        
        # Get target user's ratings as Series
        target_user_ratings = user_item_matrix.loc[user_id]
        
        # Calculate similarities with all other users
        similarities = {}
        for other_user in user_item_matrix.index:
            if other_user != user_id:
                other_user_ratings = user_item_matrix.loc[other_user]
                sim = calculate_user_similarity(target_user_ratings, other_user_ratings)
                if sim > 0:
                    similarities[other_user] = sim
        
        if not similarities:
            return "No similar users found to generate recommendations."
        
        # Generate predictions for unrated items
        predictions = {}
        all_items = set(ratings_df['item_id'].unique())
        unrated_items = all_items - rated_items
        
        for item in unrated_items:
            # Get ratings from similar users for this item
            item_ratings = ratings_df[
                (ratings_df['item_id'] == item) & 
                (ratings_df['user_id'].isin(similarities.keys()))
            ]
            
            if len(item_ratings) == 0:
                continue
            
            # Weighted average using similarity scores
            weighted_sum = 0.0
            similarity_sum = 0.0
            
            for _, row in item_ratings.iterrows():
                other_user = row['user_id']
                rating = row['rating']
                sim = similarities[other_user]
                
                weighted_sum += rating * sim
                similarity_sum += sim
            
            if similarity_sum > 0:
                predictions[item] = weighted_sum / similarity_sum
        
        # Sort and get top N
        sorted_predictions = sorted(
            predictions.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:top_n]
        
        # Format result
        result = {
            'user_id': user_id,
            'recommendations': [
                {'item_id': int(item), 'predicted_rating': float(rating)}
                for item, rating in sorted_predictions
            ]
        }
        
        return str(result)
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def add_rating(user_id: int, item_id: int, rating: float) -> str:
    """
    Add a new rating to the system.
    
    Args:
        user_id: ID of the user
        item_id: ID of the item being rated
        rating: Rating value (typically 1-5)
    
    Returns:
        Confirmation message
    """
    global ratings_df
    
    try:
        if ratings_df is None:
            return "Error: Data not loaded."
        
        # Validate rating
        if not (1.0 <= rating <= 5.0):
            return "Error: Rating must be between 1 and 5."
        
        # Check if rating already exists
        existing = ratings_df[
            (ratings_df['user_id'] == user_id) & 
            (ratings_df['item_id'] == item_id)
        ]
        
        if len(existing) > 0:
            # Update existing rating
            ratings_df.loc[
                (ratings_df['user_id'] == user_id) & 
                (ratings_df['item_id'] == item_id),
                'rating'
            ] = rating
            message = f"Updated rating: User {user_id} rated Item {item_id} as {rating}"
        else:
            # Add new rating
            new_rating = pd.DataFrame({
                'user_id': [user_id],
                'item_id': [item_id],
                'rating': [rating]
            })
            ratings_df = pd.concat([ratings_df, new_rating], ignore_index=True)
            message = f"Added rating: User {user_id} rated Item {item_id} as {rating}"
        
        # Save to file
        ratings_df.to_csv(DATA_PATH, index=False)
        logger.info(message)
        
        return message
        
    except Exception as e:
        logger.error(f"Error adding rating: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def get_similar_users(user_id: int, top_n: int = 5) -> str:
    """
    Find the most similar users to a given user based on rating patterns.
    
    Args:
        user_id: ID of the user to find similar users for
        top_n: Number of similar users to return (default: 5)
    
    Returns:
        JSON string with similar users and similarity scores
    """
    try:
        if ratings_df is None:
            return "Error: Data not loaded."
        
        # Create user-item matrix
        user_item_matrix = ratings_df.pivot_table(
            index='user_id',
            columns='item_id',
            values='rating'
        )
        
        if user_id not in user_item_matrix.index:
            return f"Error: User {user_id} not found."
        
        # Get target user's ratings
        target_user_ratings = user_item_matrix.loc[user_id]
        
        # Calculate similarities
        similarities = []
        for other_user in user_item_matrix.index:
            if other_user != user_id:
                other_user_ratings = user_item_matrix.loc[other_user]
                sim = calculate_user_similarity(target_user_ratings, other_user_ratings)
                if sim > 0:
                    similarities.append((other_user, sim))
        
        # Sort and get top N
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_similar = similarities[:top_n]
        
        result = {
            'user_id': user_id,
            'similar_users': [
                {'user_id': int(uid), 'similarity_score': float(score)}
                for uid, score in top_similar
            ]
        }
        
        return str(result)
        
    except Exception as e:
        logger.error(f"Error finding similar users: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def get_user_stats(user_id: int) -> str:
    """
    Get statistics about a user's rating behavior.
    
    Args:
        user_id: ID of the user
    
    Returns:
        JSON string with user statistics
    """
    try:
        if ratings_df is None:
            return "Error: Data not loaded."
        
        user_ratings = ratings_df[ratings_df['user_id'] == user_id]
        
        if len(user_ratings) == 0:
            return f"Error: User {user_id} has no ratings."
        
        stats = {
            'user_id': user_id,
            'total_ratings': int(len(user_ratings)),
            'average_rating': float(user_ratings['rating'].mean()),
            'min_rating': float(user_ratings['rating'].min()),
            'max_rating': float(user_ratings['rating'].max()),
            'rated_items': user_ratings['item_id'].tolist()
        }
        
        return str(stats)
        
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        return f"Error: {str(e)}"


def main():
    """Initialize and run the MCP server."""
    # Load data at startup
    load_or_initialize_data()
    
    logger.info("Starting Recommender Systems MCP Server...")
    logger.info("Available tools: get_recommendations, add_rating, get_similar_users, get_user_stats")
    
    # Run server with STDIO transport (as per MCP guidelines)
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
