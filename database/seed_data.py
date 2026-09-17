import sys
import os
from pathlib import Path
# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
from app.database import get_db, init_db
from app.models import Blog, Portfolio, Service, Inquiry, Subscriber
def seed_all():
    print("[*] Initializing database schema...")
    init_db(run_seed=False)
    conn = get_db()
    cursor = conn.cursor()
    # 1. Seed Blogs if empty
    cursor.execute("SELECT COUNT(*) FROM blogs")
    if cursor.fetchone()[0] == 0:
        print("[*] Seeding blogs...")
        blogs = [
            {
                "title": "Dominate the Namma Bengaluru Market: A Local SEO Guide for Local Businesses",
                "slug": "dominate-namma-bengaluru-market-local-seo",
                "category": "Local SEO",
                "author": "Storyworks Studio",
                "published_date": "FEB 19, 2026",
                "cover_image": "assets/blogs/a1.jpg",
                "excerpt": "If your business is not showing up when someone searches for your service in Bengaluru, you are losing customers in real time. Every day, potential buyers are searching for exactly what you offer.",
                "content": """If your business is not showing up when someone searches for your service in Bengaluru, you are losing customers in real time. Every day, potential buyers are searching for exactly what you offer and they are choosing from the businesses that appear first, not necessarily the ones that are best. Local SEO is not a marketing add-on anymore, it is the primary way high-intent customers discover and decide. In a city like Bengaluru, where convenience drives decisions and competition is dense across almost every category, ranking in local search directly impacts revenue.
The most valuable real estate on Google today is the map pack, where three businesses capture the majority of clicks, calls and visits. If you are not there, you are competing for residual attention, which rarely converts at the same rate.""",
                "status": "published",
            },
            {
                "title": "Stop Buying Likes & Start Driving Sales: The ROI-First Social Media Strategy",
                "slug": "stop-buying-likes-start-driving-sales",
                "category": "Performance Marketing",
                "author": "Storyworks Studio",
                "published_date": "FEB 25, 2026",
                "cover_image": "assets/blogs/b1.jpg",
                "excerpt": "Most businesses put money into social media with the hope that being seen will lead to sales, but in reality, a lot of marketing spend goes to waste without an ROI-driven architecture.",
                "content": """Most businesses put money into social media with the hope that being seen will lead to sales, but in reality, a lot of vanity metrics distract from what actually moves the needle. A high follower count and thousands of likes don't pay payroll—conversions and customer acquisition do.
Our ROI-first framework focuses on audience intent, high-converting creative hooks, and frictionless purchase or inquiry funnels.""",
                "status": "published",
            },
            {
                "title": "Why Your Beautiful Website Is Losing Customers (And How to Fix It)",
                "slug": "why-your-website-is-losing-customers",
                "category": "Web Design & CRO",
                "author": "Storyworks Studio",
                "published_date": "MAR 07, 2026",
                "cover_image": "assets/blogs/c1.jpg",
                "excerpt": "A well-designed website can make a strong first impression, but design alone doesn't guarantee sales. Here is why pretty websites fail and how conversion architecture solves it.",
                "content": """A well-designed website can make a strong first impression, but aesthetic design alone does not guarantee business results. If users find navigation confusing, loading speeds slow, or value propositions vague, they bounce within 3 seconds.
Fixing this requires marrying visual elegance with clear user journeys, prominent calls to action, and technical speed optimization.""",
                "status": "published",
            },
            {
                "title": "The Power of Visual Storytelling: How Imagery Transforms Brand Equity",
                "slug": "power-of-visual-storytelling",
                "category": "Brand Photography",
                "author": "Storyworks Studio",
                "published_date": "MAR 14, 2026",
                "cover_image": "assets/blogs/a1.jpg",
                "excerpt": "In an era of fleeting attention spans, consumers process imagery 60,000 times faster than text. High-caliber photography and visual craft are your brand's ultimate differentiator.",
                "content": """In an era of fleeting attention spans, visual storytelling is the fastest way to communicate prestige, craftsmanship, and trustworthiness. 
Stock photography degrades brand credibility. Bespoke product photography and art direction create distinct emotional resonance that commands premium pricing.""",
                "status": "published",
            },
            {
                "title": "Building a Distinct Brand Voice in a Crowded Digital Landscape",
                "slug": "building-a-distinct-brand-voice",
                "category": "Brand Strategy",
                "author": "Storyworks Studio",
                "published_date": "MAR 21, 2026",
                "cover_image": "assets/blogs/b1.jpg",
                "excerpt": "When all competitors offer similar features, personality becomes your greatest competitive moat. Discover how to define and deploy an unmistakable brand voice.",
                "content": """When features can be copied overnight, your voice and identity become your greatest competitive moat. Great brands do not try to speak to everyone—they speak deeply and authentically to their chosen community with conviction and style.""",
                "status": "published",
            },
            {
                "title": "Data-Driven Creative: Balancing Art and Analytics for Sustained Growth",
                "slug": "data-driven-creative-growth",
                "category": "Digital Growth",
                "author": "Storyworks Studio",
                "published_date": "MAR 28, 2026",
                "cover_image": "assets/blogs/c1.jpg",
                "excerpt": "Creative without analytics is guesswork; analytics without creative is soulless. Here is how Storyworks bridges the gap between artistic instinct and quantitative metrics.",
                "content": """The most successful brand campaigns of 2026 operate at the intersection of emotional resonance and empirical feedback. By measuring engagement signals and testing variations systematically, creative teams can scale what truly resonates.""",
                "status": "published",
            },
        ]
        for b in blogs:
            Blog.create(b)
        print(f"[OK] Seeded {len(blogs)} blog articles.")
    # 2. Seed Portfolio if empty
    cursor.execute("SELECT COUNT(*) FROM portfolio")
    if cursor.fetchone()[0] == 0:
        print("[*] Seeding portfolio case studies...")
        portfolio_items = [
            {
                "title": "Shaanvi Heritage",
                "slug": "shaanvi-heritage",
                "client": "Shaanvi",
                "category": "Branding & Packaging",
                "badge": "Shaanvi",
                "cover_image": "assets/images/portfolio/hp/4.jpg",
                "quote": "We finally have a brand voice that feels as premium as our products. The level of intentionality in every design choice has given our team a clear North Star for all future growth.",
                "short_desc": "End-to-end brand identity, packaging design, and visual art direction for premium organic foods.",
                "full_desc": "Comprehensive brand overhaul establishing Shaanvi as an artisanal culinary benchmark in South India.",
                "year": "2026",
                "project_url": "1_shaanvi.html",
                "is_featured": 1,
                "status": "published",
            },
            {
                "title": "Mantras Wellness",
                "slug": "mantras-wellness",
                "client": "Mantras",
                "category": "Brand Strategy & Identity",
                "badge": "Mantras",
                "cover_image": "assets/images/portfolio/hp/2.jpg",
                "quote": "Storyworks redefined our presence in the holistic health sector with clarity and unmatched elegance.",
                "short_desc": "Holistic brand positioning and serene packaging for modern wellness lifestyle products.",
                "full_desc": "Created a multi-sensory brand experience reflecting tranquility, purity, and mindful living.",
                "year": "2026",
                "project_url": "2_mantras.html",
                "is_featured": 1,
                "status": "published",
            },
            {
                "title": "PickleJar Traditional Flavors",
                "slug": "picklejar-traditional-flavors",
                "client": "PickleJar",
                "category": "Packaging & Art Direction",
                "badge": "PickleJar",
                "cover_image": "assets/images/portfolio/hp/3.jpg",
                "quote": "Our retail shelf pickup doubled within 60 days of the packaging redesign.",
                "short_desc": "Nostalgic culinary roots reimagined with vibrant modern shelf appeal.",
                "full_desc": "Custom illustrated labels, bespoke glass jar typography, and vibrant color palettes.",
                "year": "2025",
                "project_url": "3_picklejar.html",
                "is_featured": 1,
                "status": "published",
            },
            {
                "title": "B-Ship Maritime Logistics",
                "slug": "b-ship-logistics",
                "client": "Bship",
                "category": "Corporate Digital Identity",
                "badge": "Bship",
                "cover_image": "assets/images/portfolio/hp/1.jpg",
                "quote": "A tech-forward digital experience that mirrors our global logistics capability.",
                "short_desc": "High-impact visual identity and interactive web experience for freight & maritime operations.",
                "full_desc": "Streamlined client portal UI and commanding typographic hierarchy for enterprise logistics.",
                "year": "2026",
                "project_url": "4_bship.html",
                "is_featured": 1,
                "status": "published",
            },
            {
                "title": "Fishland Seafoods",
                "slug": "fishland-seafoods",
                "client": "Fishland",
                "category": "Retail & Environmental Branding",
                "badge": "Fishland",
                "cover_image": "assets/images/portfolio/hp/5.jpg",
                "quote": "Fresh, contemporary, and unforgettable in every retail touchpoint.",
                "short_desc": "Coastal culinary branding, retail store graphics, and fresh seafood packaging.",
                "full_desc": "Modern maritime aesthetics bringing coastal freshness into metropolitan dining.",
                "year": "2025",
                "project_url": "5_fishland.html",
                "is_featured": 1,
                "status": "published",
            },
            {
                "title": "Bhruhadrupi Temple Heritage",
                "slug": "bhruhadrupi-temple-heritage",
                "client": "Bhruhadrupi",
                "category": "Architectural Visuals & Print",
                "badge": "Bhruhadrupi",
                "cover_image": "assets/images/portfolio/hp/6.jpg",
                "quote": "Sacred heritage immortalized with precision, respect, and breathtaking artistry.",
                "short_desc": "Sacred architecture documentation, commemorative coffee table book, and cultural preservation.",
                "full_desc": "Rich archival photography, gold-foil embossed typography, and architectural schematics.",
                "year": "2025",
                "project_url": "6_temple.html",
                "is_featured": 1,
                "status": "published",
            },
            {
                "title": "SBL Food Innovations",
                "slug": "sbl-foods",
                "client": "SBL-Foods",
                "category": "FMCG Brand Architecture",
                "badge": "SBL-Foods",
                "cover_image": "assets/images/portfolio/hp/7.jpg",
                "quote": "Helped consolidate our multi-line enterprise under one cohesive powerhouse brand.",
                "short_desc": "Multi-category FMCG packaging suite and corporate brand architecture.",
                "full_desc": "End-to-end design for snacks, staples, and packaged foods across national retail chains.",
                "year": "2026",
                "project_url": "7_sblfood.html",
                "is_featured": 0,
                "status": "published",
            },
            {
                "title": "SBL Agro & Farms",
                "slug": "sbl-farms",
                "client": "SBL-Farms",
                "category": "Sustainable Agri-Branding",
                "badge": "SBL-Farms",
                "cover_image": "assets/images/portfolio/hp/8.jpg",
                "quote": "Connected our farm-to-table ethos directly with discerning conscious buyers.",
                "short_desc": "Organic farming branding, farm-gate packaging, and environmental storytelling.",
                "full_desc": "Celebration of sustainable agriculture and regenerative farming practices.",
                "year": "2025",
                "project_url": "8_farms.html",
                "is_featured": 0,
                "status": "published",
            },
            {
                "title": "Achuthan Publications",
                "slug": "achuthan-editorial",
                "client": "Achuthan",
                "category": "Editorial & Book Design",
                "badge": "Achuthan",
                "cover_image": "assets/images/portfolio/hp/9.jpg",
                "quote": "Masterful typesetting and binding that honors the written word.",
                "short_desc": "Fine typography, custom book covers, and artisanal print binding.",
                "full_desc": "Meticulous typesetting, bespoke chapter openers, and heirloom cover treatments.",
                "year": "2025",
                "project_url": "9_book.html",
                "is_featured": 0,
                "status": "published",
            },
        ]
        for p in portfolio_items:
            Portfolio.create(p)
        print(f"[OK] Seeded {len(portfolio_items)} portfolio projects.")
    # 3. Seed Services if empty
    cursor.execute("SELECT COUNT(*) FROM services")
    if cursor.fetchone()[0] == 0:
        print("[*] Seeding agency services...")
        services_data = [
            {
                "title": "Brand Strategy",
                "slug": "brand-strategy",
                "short_desc": "We move beyond aesthetics to architect the strategic soul of your business. By synthesizing market intelligence with intuition, we build the narrative frameworks that drive your brand’s future.",
                "full_desc": "We move beyond aesthetics to architect the strategic soul of your business. By synthesizing market intelligence with intuition, we build the narrative frameworks that drive your brand’s future.",
                "icon": "fas fa-chart-line",
                "display_order": 1,
                "is_active": 1,
            },
            {
                "title": "Brand Identity & Design",
                "slug": "brand-identity-design",
                "short_desc": "We craft visual legacies through intentional design, from signature logos to multi-sensory systems. Every touchpoint is engineered for flawless consistency, creating a timeless invitation into your brand’s world.",
                "full_desc": "We craft visual legacies through intentional design, from signature logos to multi-sensory systems. Every touchpoint is engineered for flawless consistency, creating a timeless invitation into your brand’s world.",
                "icon": "fas fa-search",
                "display_order": 2,
                "is_active": 1,
            },
            {
                "title": "Content & Copywriting",
                "slug": "content-copywriting",
                "short_desc": "Our narratives do more than fill space; they command attention and build lasting rapport. We translate complex value propositions into persuasive human stories that sell a philosophy, not just a product.",
                "full_desc": "Our narratives do more than fill space; they command attention and build lasting rapport. We translate complex value propositions into persuasive human stories that sell a philosophy, not just a product.",
                "icon": "fas fa-thumbs-up",
                "display_order": 3,
                "is_active": 1,
            },
            {
                "title": "Digital Marketing",
                "slug": "digital-marketing",
                "short_desc": "Our approach integrates high-intent SEO and strategic social storytelling into performance-driven ecosystems that grow your community and your revenue in equal measure.",
                "full_desc": "Our approach integrates high-intent SEO and strategic social storytelling into performance-driven ecosystems that grow your community and your revenue in equal measure.",
                "icon": "fab fa-google",
                "display_order": 4,
                "is_active": 1,
            },
            {
                "title": "Web & Experience Design",
                "slug": "web-experience-design",
                "short_desc": "We view the digital interface as a premier storefront. Our team designs high-conversion digital environments where elegant minimalism meets functional rigor, ensuring every click feels intuitive and every interaction reinforces trust.",
                "full_desc": "We view the digital interface as a premier storefront. Our team designs high-conversion digital environments where elegant minimalism meets functional rigor, ensuring every click feels intuitive and every interaction reinforces trust.",
                "icon": "fas fa-laptop-code",
                "display_order": 5,
                "is_active": 1,
            },
            {
                "title": "Launch & Campaign Strategy",
                "slug": "launch-campaign-strategy",
                "short_desc": "We transform entries into arrivals through strategic blueprints and high-impact storytelling. By orchestrating the pivotal moments where brands meet the world, we ensure your debut is both seen and felt.",
                "full_desc": "We transform entries into arrivals through strategic blueprints and high-impact storytelling. By orchestrating the pivotal moments where brands meet the world, we ensure your debut is both seen and felt.",
                "icon": "fas fa-code",
                "display_order": 6,
                "is_active": 1,
            },
        ]
        for s in services_data:
            Service.create(s)
        print(f"[OK] Seeded {len(services_data)} services.")
    # 4. Seed initial sample inquiries if empty
    cursor.execute("SELECT COUNT(*) FROM inquiries")
    if cursor.fetchone()[0] == 0:
        print("[*] Seeding sample inquiry...")
        Inquiry.create({
            "first_name": "Vikram",
            "last_name": "Rao",
            "email": "vikram@kaveribeverages.com",
            "phone": "+91 98450 11223",
            "company": "Kaveri Beverages",
            "budget": "₹2,00,000 – ₹5,00,000",
            "services": "Branding, Packaging, Photography",
            "message": "We are launching a premium artisanal iced tea brand in Bengaluru next quarter. We need full packaging design for 4 SKUs, complete visual identity, and product launch photography.",
            "ip_address": "127.0.0.1",
        })
        print("[OK] Seeded sample inquiry.")
    # 5. Seed sample subscriber if empty
    cursor.execute("SELECT COUNT(*) FROM subscribers")
    if cursor.fetchone()[0] == 0:
        Subscriber.add("design-trends@storyworks.studio")
        print("[OK] Seeded sample newsletter subscriber.")
    conn.close()
    print("[*] All seeding completed successfully!")
if __name__ == "__main__":
    seed_all()
