"""
Database seeding script to populate the database with sample data.

This script creates sample users, posts, and votes for testing and development.
Run this script after creating the database tables to populate them with data.

Usage:
    python seed_db.py
"""

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
from app.utils import hash_password
from datetime import datetime, timedelta, timezone

# Sample users data
SAMPLE_USERS = [
    {
        "email": "john@example.com",
        "password": "password123"
    },
    {
        "email": "jane@example.com",
        "password": "securepass456"
    },
    {
        "email": "bob@example.com",
        "password": "bobpass789"
    },
]

# Sample posts data (user index, not ID - will be resolved after users are created)
SAMPLE_POSTS = [
    {
        "title": "Welcome to My Blog",
        "content": "This is my first blog post. I'm excited to share my thoughts and ideas with you all!",
        "published": True,
        "user_index": 0  # John's posts
    },
    {
        "title": "FastAPI Tips and Tricks",
        "content": "Learn how to build fast and reliable APIs using FastAPI framework. It's a modern web framework for building APIs with Python.",
        "published": True,
        "user_index": 0  # John's posts
    },
    {
        "title": "Database Design Best Practices",
        "content": "In this post, I'll share some best practices for designing efficient and scalable databases.",
        "published": True,
        "user_index": 1  # Jane's posts
    },
    {
        "title": "Getting Started with SQLAlchemy",
        "content": "SQLAlchemy is a powerful Python SQL toolkit and Object Relational Mapper (ORM). Let's explore its features!",
        "published": True,
        "user_index": 1  # Jane's posts
    },
    {
        "title": "Understanding JWT Tokens",
        "content": "JWT (JSON Web Tokens) are a popular way to implement authentication in web applications. Here's how they work...",
        "published": True,
        "user_index": 2  # Bob's posts
    },
]

# Sample votes data (user_index, post_index)
SAMPLE_VOTES = [
    {"user_index": 0, "post_index": 2},  # John likes Jane's first post
    {"user_index": 0, "post_index": 3},  # John likes Jane's second post
    {"user_index": 1, "post_index": 0},  # Jane likes John's first post
    {"user_index": 1, "post_index": 4},  # Jane likes Bob's post
    {"user_index": 2, "post_index": 0},  # Bob likes John's first post
    {"user_index": 2, "post_index": 1},  # Bob likes John's second post
]


def seed_database():
    """
    Populate the database with sample data.

    This function:
    1. Deletes existing data (if any) to ensure clean state
    2. Creates sample users with hashed passwords
    3. Creates sample posts associated with users
    4. Creates sample votes linking users to posts
    """
    # Create database tables if they don't exist
    models.Base.metadata.create_all(bind=engine)

    # Get database session
    db = SessionLocal()

    try:
        # Clear existing data
        print("Clearing existing data...")
        db.query(models.Votes).delete()
        db.query(models.Post).delete()
        db.query(models.User).delete()
        db.commit()
        print("✓ Existing data cleared")

        # Create and insert users
        print("\nCreating users...")
        users = []
        for user_data in SAMPLE_USERS:
            # Hash the password before storing
            user = models.User(
                email=user_data["email"],
                password=hash_password(user_data["password"])
            )
            db.add(user)
            users.append(user)

        # Flush to ensure users are assigned IDs before creating posts
        db.flush()
        db.commit()
        print(f"✓ Created {len(users)} users")

        # Create and insert posts
        print("\nCreating posts...")
        posts = []
        for post_data in SAMPLE_POSTS:
            # Use the actual user object instead of hardcoded user_id
            user = users[post_data["user_index"]]
            post = models.Post(
                title=post_data["title"],
                content=post_data["content"],
                published=post_data["published"],
                owner=user  # Use the relationship instead of user_id
            )
            db.add(post)
            posts.append(post)

        # Flush to ensure posts are assigned IDs before creating votes
        db.flush()
        db.commit()
        print(f"✓ Created {len(posts)} posts")

        # Create and insert votes
        print("\nCreating votes...")
        votes = []
        for vote_data in SAMPLE_VOTES:
            # Use the actual user and post objects
            user = users[vote_data["user_index"]]
            post = posts[vote_data["post_index"]]
            vote = models.Votes(
                user_id=user.id,
                post_id=post.id
            )
            db.add(vote)
            votes.append(vote)

        db.commit()
        print(f"✓ Created {len(votes)} votes")

        # Print summary
        print("\n" + "="*50)
        print("DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("="*50)
        print(f"✓ Users: {len(users)}")
        print(f"✓ Posts: {len(posts)}")
        print(f"✓ Votes: {len(votes)}")
        print("\nSample Credentials:")
        for user in SAMPLE_USERS:
            print(f"  - Email: {user['email']}, Password: {user['password']}")

    except Exception as e:
        print(f"✗ Error seeding database: {e}")
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
