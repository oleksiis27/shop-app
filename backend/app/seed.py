import random

from faker import Faker
from sqlalchemy import select

from app.database import SessionLocal, engine, Base
from app.models.category import Category
from app.models.product import Product
from app.models.user import User
from app.services.auth_service import hash_password

fake = Faker()

CATEGORIES = [
    {"name": "Electronics", "slug": "electronics"},
    {"name": "Clothing", "slug": "clothing"},
    {"name": "Books", "slug": "books"},
    {"name": "Home & Garden", "slug": "home-garden"},
    {"name": "Sports", "slug": "sports"},
    {"name": "Toys", "slug": "toys"},
]

# Realistic product templates per category
PRODUCT_TEMPLATES = {
    "Electronics": [
        ("Wireless Bluetooth Headphones", "Premium noise-cancelling headphones with 30-hour battery life"),
        ("USB-C Fast Charger 65W", "GaN charger compatible with laptops, tablets, and phones"),
        ("Mechanical Keyboard RGB", "Hot-swappable switches with per-key RGB lighting"),
        ("Portable SSD 1TB", "High-speed external storage with USB 3.2 Gen 2"),
        ("Smart Watch Pro", "Fitness tracker with heart rate monitor and GPS"),
        ("Webcam 4K Ultra HD", "Auto-focus webcam with built-in microphone for streaming"),
        ("Wireless Mouse Ergonomic", "Vertical design mouse with adjustable DPI"),
        ("Monitor Stand Aluminum", "Adjustable monitor riser with USB hub"),
        ("Power Bank 20000mAh", "Fast-charging portable battery with LED display"),
        ("Noise Cancelling Earbuds", "True wireless earbuds with active noise cancellation"),
    ],
    "Clothing": [
        ("Classic Cotton T-Shirt", "Comfortable 100% cotton crew neck t-shirt"),
        ("Slim Fit Jeans", "Stretch denim jeans with modern slim fit"),
        ("Hooded Sweatshirt", "Warm fleece hoodie with kangaroo pocket"),
        ("Running Shoes Lightweight", "Breathable mesh sneakers for daily running"),
        ("Leather Belt Premium", "Genuine leather belt with classic buckle"),
        ("Winter Down Jacket", "Insulated puffer jacket for cold weather"),
        ("Casual Polo Shirt", "Pique cotton polo with embroidered logo"),
        ("Athletic Shorts", "Quick-dry shorts with zip pockets"),
        ("Wool Beanie Hat", "Soft knit beanie for winter warmth"),
        ("Canvas Sneakers", "Classic low-top canvas shoes with rubber sole"),
    ],
    "Books": [
        ("Python Programming Mastery", "Complete guide to advanced Python development"),
        ("Clean Code Handbook", "Best practices for writing maintainable software"),
        ("Data Science Fundamentals", "Introduction to statistics and machine learning"),
        ("JavaScript: The Good Parts", "Essential patterns for modern JavaScript"),
        ("System Design Interview", "Comprehensive guide to system design questions"),
        ("The Art of Testing", "Practical approach to software quality assurance"),
        ("DevOps Engineering", "CI/CD pipelines and infrastructure as code"),
        ("Algorithm Design Manual", "Problem-solving strategies for competitive programming"),
        ("Database Internals", "Deep dive into storage engines and distributed systems"),
        ("Microservices Patterns", "Architecture patterns for distributed applications"),
    ],
    "Home & Garden": [
        ("Stainless Steel Water Bottle", "Double-wall insulated bottle keeps drinks cold 24h"),
        ("LED Desk Lamp Dimmable", "Touch control desk lamp with USB charging port"),
        ("Indoor Plant Pot Set", "Set of 3 ceramic pots with drainage holes"),
        ("Memory Foam Pillow", "Ergonomic contour pillow for neck support"),
        ("Kitchen Knife Set", "5-piece professional chef knife set with block"),
        ("Scented Candle Collection", "Set of 4 soy wax candles with natural fragrances"),
        ("Bamboo Cutting Board", "Large organic bamboo board with juice groove"),
        ("Smart LED Light Bulb", "WiFi-enabled color changing bulb with app control"),
        ("Cotton Bath Towel Set", "Pack of 4 plush bath towels 600 GSM"),
        ("Wall Clock Minimalist", "Silent quartz clock with modern Scandinavian design"),
    ],
    "Sports": [
        ("Yoga Mat Premium", "Non-slip 6mm thick exercise mat with carrying strap"),
        ("Resistance Bands Set", "5 latex bands with different resistance levels"),
        ("Foam Roller Muscle", "High-density foam roller for deep tissue massage"),
        ("Jump Rope Speed", "Adjustable steel cable rope with ball bearings"),
        ("Dumbbell Set Adjustable", "Pair of adjustable dumbbells 5-25 lbs each"),
        ("Fitness Tracker Band", "Waterproof activity tracker with sleep monitoring"),
        ("Protein Shaker Bottle", "BPA-free mixer bottle with blending ball"),
        ("Gym Gloves Padded", "Breathable workout gloves with wrist support"),
        ("Ab Roller Wheel", "Core trainer with knee pad included"),
        ("Tennis Racket Pro", "Graphite composite racket with vibration dampening"),
    ],
    "Toys": [
        ("Building Blocks 500pc", "Creative construction set for ages 6+"),
        ("RC Car Off-Road", "4WD remote control truck with rechargeable battery"),
        ("Board Game Strategy", "Award-winning strategy game for 2-4 players"),
        ("Puzzle 1000 Pieces", "Scenic landscape jigsaw puzzle for adults"),
        ("Drone with Camera", "Mini quadcopter with HD camera and altitude hold"),
        ("Card Game Collection", "Classic card games set with premium cards"),
        ("Science Experiment Kit", "50 experiments for young scientists ages 8+"),
        ("Plush Teddy Bear", "Soft stuffed animal 18 inches with ribbon"),
        ("Magic Cube Speed", "Professional 3x3 speed cube with smooth rotation"),
        ("Art Supply Kit", "Complete drawing set with pencils, markers, and paper"),
    ],
}


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        existing = db.execute(select(User).limit(1)).scalar_one_or_none()
        if existing:
            print("Database already seeded, skipping.")
            return

        # Create users
        admin = User(
            email="admin@shop.com",
            password_hash=hash_password("admin123"),
            name="Admin User",
            role="admin",
        )
        user = User(
            email="user@shop.com",
            password_hash=hash_password("user123"),
            name="John Doe",
            role="user",
        )
        db.add_all([admin, user])
        db.flush()
        print(f"Created users: admin@shop.com, user@shop.com")

        # Create categories
        category_map = {}
        for cat_data in CATEGORIES:
            cat = Category(**cat_data)
            db.add(cat)
            db.flush()
            category_map[cat.name] = cat
        print(f"Created {len(CATEGORIES)} categories")

        # Create products
        product_count = 0
        for cat_name, templates in PRODUCT_TEMPLATES.items():
            category = category_map[cat_name]
            for name, description in templates:
                product = Product(
                    name=name,
                    description=description,
                    price=round(random.uniform(5.99, 299.99), 2),
                    stock=random.randint(5, 200),
                    category_id=category.id,
                    image_url=f"https://picsum.photos/seed/{fake.slug()}/400/400",
                )
                db.add(product)
                product_count += 1

        db.commit()
        print(f"Created {product_count} products")
        print("Seed completed successfully!")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
