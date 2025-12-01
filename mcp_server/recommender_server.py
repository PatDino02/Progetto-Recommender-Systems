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
movies_df: pd.DataFrame = None
DATA_PATH = Path(__file__).parent.parent / "data" / "ratings.csv"
MOVIES_PATH = Path(__file__).parent.parent / "data" / "movies.csv"


def load_or_initialize_data():
    """Load ratings data or initialize with sample data."""
    global ratings_df, movies_df
    
    try:
        if DATA_PATH.exists():
            ratings_df = pd.read_csv(DATA_PATH)
            logger.info(f"Loaded {len(ratings_df)} ratings from {DATA_PATH}")
        
        # Load movies mapping if exists
        if MOVIES_PATH.exists():
            movies_df = pd.read_csv(MOVIES_PATH)
            logger.info(f"Loaded {len(movies_df)} movies from {MOVIES_PATH}")
            
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise


def calculate_user_similarity(user1_ratings: pd.Series, user2_ratings: pd.Series) -> float:
    """
    Calculate Pearson correlation between two users based on common rated items.
    
    Args:
        user1_ratings: Ratings of user 1
        user2_ratings: Ratings of user 2
    
    Returns:
        Similarity score between -1 and 1 (normalized to 0-1)
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
    
    # Need at least 2 items for correlation
    if len(r1) < 2:
        return 0.0
    
    # Calculate means
    mean1 = np.mean(r1)
    mean2 = np.mean(r2)
    
    # Center the ratings
    r1_centered = r1 - mean1
    r2_centered = r2 - mean2
    
    # Calculate Pearson correlation
    numerator = np.sum(r1_centered * r2_centered)
    denominator = np.sqrt(np.sum(r1_centered ** 2) * np.sum(r2_centered ** 2))
    
    if denominator == 0:
        return 0.0
    
    correlation = numerator / denominator
    
    # Normalize from [-1, 1] to [0, 1] for compatibility
    return float((correlation + 1) / 2)


@mcp.tool()
async def get_recommendations(user_id: int, top_n: int = 5) -> str:
    """
    Get top N item recommendations for a user using collaborative filtering.
    Uses user-based collaborative filtering with Pearson correlation.
    
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
        
        # Format result with movie titles if available
        result = {
            'user_id': user_id,
            'recommendations': []
        }
        
        for item, rating in sorted_predictions:
            rec_item = {
                'item_id': int(item),
                'predicted_rating': float(rating)
            }
            
            # Add movie title if available
            if movies_df is not None:
                movie_info = movies_df[movies_df['item_id'] == item]
                if not movie_info.empty:
                    rec_item['title'] = movie_info.iloc[0]['title']
            
            result['recommendations'].append(rec_item)
        
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
                    # Count common items (both rated)
                    common_items = (~target_user_ratings.isna() & ~other_user_ratings.isna()).sum()
                    similarities.append((other_user, sim, common_items))
        
        # Sort and get top N
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_similar = similarities[:top_n]
        
        result = {
            'user_id': user_id,
            'similar_users': [
                {
                    'user_id': int(uid), 
                    'similarity_score': float(score),
                    'common_items': int(common)
                }
                for uid, score, common in top_similar
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
