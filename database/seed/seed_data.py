import os
import sys
import random
import bcrypt
from datetime import datetime, date, timedelta, timezone

# Ensure apps/api is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
sys.path.insert(0, os.path.join(project_root, "apps", "api"))

from app.core.database import engine, SessionLocal, Base
from app.models.user import User
from app.models.erp import Branch, Category, Product, Customer, Supplier, Sale, SaleItem, Purchase, Inventory
from app.models.audit import AuditLog

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=10)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def seed_database(num_sales: int = 50000):
    random.seed(42)  # Deterministic seed

    print(f"Creating database tables on {engine.url}...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        print("1. Seeding Branches...")
        branches_data = [
            {"name": "Muscat", "city": "Muscat", "region": "Capital"},
            {"name": "Salalah", "city": "Salalah", "region": "Dhofar"},
            {"name": "Sohar", "city": "Sohar", "region": "Al Batinah"},
            {"name": "Nizwa", "city": "Nizwa", "region": "Ad Dakhiliyah"},
        ]
        branch_objs = []
        for b in branches_data:
            obj = Branch(**b)
            session.add(obj)
            branch_objs.append(obj)
        session.commit()
        for b in branch_objs:
            session.refresh(b)
        branch_ids = [b.id for b in branch_objs]
        muscat_id = branch_ids[0]

        print("2. Seeding Demo Users...")
        demo_password_hash = hash_password("Demo@12345")
        users_data = [
            {
                "email": "admin@mmi-demo.com",
                "password_hash": demo_password_hash,
                "full_name": "MMI System Administrator",
                "role": "Admin",
                "branch_id": None,
                "is_active": True,
            },
            {
                "email": "manager@mmi-demo.com",
                "password_hash": demo_password_hash,
                "full_name": "Tariq Al-Balushi (Muscat Manager)",
                "role": "Branch Manager",
                "branch_id": muscat_id,
                "is_active": True,
            },
            {
                "email": "analyst@mmi-demo.com",
                "password_hash": demo_password_hash,
                "full_name": "Fatima Al-Harthy (Senior Analyst)",
                "role": "Analyst",
                "branch_id": None,
                "is_active": True,
            },
        ]
        for u in users_data:
            session.add(User(**u))
        session.commit()

        print("3. Seeding Categories...")
        categories_data = [
            ("Building Materials", "Structural steel, cement, aggregates, and insulation"),
            ("Electrical Supplies", "Cables, switchgear, LED panels, transformers"),
            ("Plumbing & Sanitary", "Piping, valves, pumps, drainage, bathroom fittings"),
            ("Industrial Tools", "Power tools, pneumatic machinery, hand tools"),
            ("Safety & PPE", "Hard hats, safety boots, high-vis vests, harnesses"),
            ("Fasteners & Hardware", "Bolts, anchors, screws, brackets"),
        ]
        category_objs = []
        for name, desc in categories_data:
            cat = Category(name=name, description=desc)
            session.add(cat)
            category_objs.append(cat)
        session.commit()
        for cat in category_objs:
            session.refresh(cat)
        cat_ids = [c.id for c in category_objs]

        print("4. Seeding 120 Products...")
        product_templates = [
            # Building Materials (cat 0)
            ("Deformed Steel Rebar 12mm", 0, 18.5, 14.0),
            ("Deformed Steel Rebar 16mm", 0, 24.0, 18.2),
            ("Portland Cement 50kg Bag", 0, 1.85, 1.40),
            ("Sulfate Resistant Cement 50kg", 0, 2.15, 1.65),
            ("Ready-Mix Mortar 25kg", 0, 1.30, 0.95),
            ("Gypsum Board 12.5mm 1.2x2.4m", 0, 3.40, 2.60),
            ("Rockwool Insulation Slab 50mm", 0, 14.50, 10.80),
            ("AAC Autoclaved Blocks 200mm", 0, 2.80, 2.10),
            ("Galvanized Corrugated Sheet 3m", 0, 8.90, 6.70),
            ("Structural Steel H-Beam 200x200", 0, 85.00, 64.00),
            ("Epoxy Tile Grout 5kg", 0, 6.20, 4.40),
            ("Waterproofing Membrane 4mm Roll", 0, 22.50, 16.80),
            ("Geotextile Non-Woven Fabric 100m", 0, 65.00, 49.00),
            ("Reinforcing Wire Mesh 6mm", 0, 19.50, 14.50),
            ("Expanded Metal Lath 2.4m", 0, 4.20, 3.10),
            ("Concrete Bonding Agent 20L", 0, 28.00, 21.00),
            ("Curing Compound Drum 200L", 0, 145.00, 110.00),
            ("Polystyrene Thermal Sheet 50mm", 0, 5.80, 4.20),
            ("Structural Hollow Section Steel", 0, 42.00, 31.50),
            ("Sandlime Brick Pallet 500pcs", 0, 75.00, 55.00),

            # Electrical (cat 1)
            ("CU/XLPE Power Cable 4x16mm 100m", 1, 160.00, 125.00),
            ("Single Core Earth Wire 10mm 100m", 1, 38.00, 29.00),
            ("Armoured Cable 3x2.5mm 100m", 1, 78.00, 59.00),
            ("Miniature Circuit Breaker 16A 1P", 1, 3.20, 2.30),
            ("MCCB 3-Pole 250A Adjustable", 1, 145.00, 108.00),
            ("Main Distribution Board 12-Way", 1, 85.00, 62.00),
            ("Modular Contactor 40A 4P", 1, 18.50, 13.80),
            ("LED Troffer Panel 60x60cm 40W", 1, 12.50, 9.00),
            ("Industrial LED High Bay 150W", 1, 48.00, 35.00),
            ("IP65 Weatherproof Switch 2-Gang", 1, 4.80, 3.40),
            ("PVC Electrical Conduit 20mm 3m", 1, 0.95, 0.68),
            ("GI Flexible Conduit 25mm 30m", 1, 18.00, 13.20),
            ("Perforated Cable Tray 200x50mm", 1, 14.50, 10.50),
            ("Solar Inverter 5kW Hybrid", 1, 420.00, 320.00),
            ("Deep Cycle Battery 12V 200Ah", 1, 110.00, 85.00),
            ("Automatic Transfer Switch 100A", 1, 195.00, 148.00),
            ("Surge Protection Device 4P 40kA", 1, 32.00, 23.50),
            ("Industrial Plug & Socket 32A 3P+E", 1, 9.50, 7.00),
            ("Copper Earth Rod 5/8 inch 2.4m", 1, 11.20, 8.10),
            ("Heat Shrink Termination Kit 11kV", 1, 92.00, 70.00),

            # Plumbing & Sanitary (cat 2)
            ("PPR Hot/Cold Pipe 25mm 4m", 2, 2.40, 1.70),
            ("PPR Ball Valve Brass Core 25mm", 2, 4.50, 3.20),
            ("UPVC Pressure Pipe Class E 110mm", 2, 12.80, 9.40),
            ("UPVC Drainage Elbow 90 Deg 110mm", 2, 1.90, 1.35),
            ("Cast Iron Submersible Sewage Pump 1HP", 2, 135.00, 100.00),
            ("Booster Pump Twin Set 1.5HP", 2, 280.00, 215.00),
            ("Gate Valve Flanged PN16 80mm", 2, 48.00, 36.00),
            ("Check Valve Dual Plate 100mm", 2, 55.00, 41.00),
            ("Water Storage Tank 500 Gal 4-Layer", 2, 120.00, 90.00),
            ("Electric Water Heater 80L Heavy Duty", 2, 46.00, 34.00),
            ("CPVC Pipe 1 inch SDR11 3m", 2, 3.80, 2.75),
            ("Commercial Sensor Basin Mixer", 2, 68.00, 49.00),
            ("Wall-Hung Ceramic WC Set", 2, 85.00, 62.00),
            ("Stainless Steel Floor Drain 15x15", 2, 7.50, 5.20),
            ("Pressure Reducing Valve 2 inch", 2, 62.00, 46.00),
            ("Y-Strainer Flanged DN80", 2, 41.00, 30.00),
            ("Expansion Joint Rubber EPDM 4 inch", 2, 29.00, 21.00),
            ("Float Switch Cable 5m", 2, 9.20, 6.70),
            ("Water Meter Multi-Jet 1 inch", 2, 24.00, 17.50),
            ("PEX-AL-PEX Multilayer Pipe 100m", 2, 54.00, 39.00),

            # Industrial Tools (cat 3)
            ("Rotary Hammer Drill SDS-Plus 850W", 3, 72.00, 53.00),
            ("Angle Grinder 230mm 2400W", 3, 65.00, 48.00),
            ("Heavy Cordless Impact Wrench 1/2 18V", 3, 98.00, 72.00),
            ("Inverter ARC Welding Machine 250A", 3, 140.00, 105.00),
            ("MIG/MAG Synergic Welder 300A", 3, 420.00, 320.00),
            ("Bench Drill Press 550W 16mm", 3, 115.00, 85.00),
            ("Air Compressor Direct 50L 2.5HP", 3, 130.00, 96.00),
            ("Hydraulic Floor Jack 3-Ton Heavy", 3, 52.00, 38.00),
            ("Torque Wrench 1/2 inch 40-210Nm", 3, 28.00, 20.00),
            ("Laser Distance Meter 80m IP54", 3, 34.00, 24.00),
            ("Self-Leveling 360 Laser Level 12-Line", 3, 78.00, 57.00),
            ("Industrial Wet/Dry Vacuum 30L", 3, 85.00, 62.00),
            ("Cut-Off Chop Saw Metal 355mm", 3, 89.00, 66.00),
            ("Electric Demolition Breaker 1600W", 3, 175.00, 130.00),
            ("Concrete Vibrator Poker 38mm 4m", 3, 92.00, 68.00),
            ("Plate Compactor Petrol 6.5HP", 3, 340.00, 260.00),
            ("Magnetic Core Drill 1200W", 3, 260.00, 195.00),
            ("Heavy Tool Chest 7-Drawer Roller", 3, 190.00, 140.00),
            ("Hand Pallet Truck 3-Ton Nylon Wheels", 3, 165.00, 122.00),
            ("Chain Block Hoist 2-Ton 3m", 3, 45.00, 33.00),

            # Safety & PPE (cat 4)
            ("Safety Helmet Vented Ratchet White", 4, 3.80, 2.60),
            ("Safety Helmet Vented Ratchet Yellow", 4, 3.80, 2.60),
            ("Safety Boots S3 Steel Toe Leather 42", 4, 16.50, 11.80),
            ("Safety Boots S3 Steel Toe Leather 43", 4, 16.50, 11.80),
            ("Full Body Safety Harness Twin Lanyard", 4, 28.00, 20.00),
            ("High-Visibility Vest Class 2 Mesh", 4, 1.80, 1.20),
            ("Welding Mask Auto-Darkening Shade 9-13", 4, 22.00, 15.50),
            ("Safety Goggles Anti-Fog Scratch Resistant", 4, 2.20, 1.50),
            ("Chemical Resistant Nitrile Gloves Pack 12", 4, 7.50, 5.20),
            ("Heavy Leather Welding Gloves", 4, 4.20, 2.90),
            ("Ear Muffs Noise Reduction 32dB", 4, 6.80, 4.80),
            ("Dust Respirator FFP2 Valve Pack 20", 4, 14.00, 9.80),
            ("Half-Facepiece Reusable Respirator Twin", 4, 24.00, 17.00),
            ("Emergency Eye Wash Station Wall Mounted", 4, 62.00, 45.00),
            ("First Aid Industrial Kit 50 Persons", 4, 29.00, 21.00),
            ("Fire Extinguisher ABC Powder 6kg", 4, 18.00, 13.00),
            ("CO2 Fire Extinguisher 5kg Trolley", 4, 45.00, 33.00),
            ("Spill Kit Universal 50L Drum", 4, 58.00, 42.00),
            ("Reflective Traffic Cone 750mm Heavy", 4, 6.20, 4.40),
            ("Safety Barrier Fence Orange 50m", 4, 14.50, 10.20),

            # Fasteners & Hardware (cat 5)
            ("Hex Bolt Grade 8.8 M12x50 Box 100", 5, 8.50, 6.00),
            ("Hex Bolt Grade 8.8 M16x70 Box 50", 5, 12.00, 8.50),
            ("Stainless Steel 316 Anchor Bolt M12", 5, 2.80, 1.95),
            ("Threaded Rod Zinc Plated 1m M16", 5, 3.20, 2.30),
            ("Self-Drilling Screw Hex Head 5.5x25 500pcs", 5, 11.50, 8.20),
            ("Drop-In Anchor M10 Zinc Box 100", 5, 9.20, 6.50),
            ("Chemical Anchor Cartridge 410ml", 5, 12.80, 9.10),
            ("Heavy Duty Wire Rope Clip 12mm", 5, 1.40, 0.95),
            ("Galvanized Turnbuckle Eye & Hook M16", 5, 4.80, 3.40),
            ("D-Shackle Stainless Steel 316 12mm", 5, 3.60, 2.50),
            ("Blind Rivet Aluminium 4.8x12 Box 1000", 5, 7.80, 5.50),
            ("Nylon Wall Plug with Screw 8mm 100pcs", 5, 3.10, 2.10),
            ("Stainless Steel Hose Clamp 2 inch Pack 10", 5, 4.20, 2.90),
            ("C-Channel Unistrut Galvanized 41x41 3m", 5, 14.20, 10.00),
            ("Beam Clamp M10 Galvanized", 5, 2.10, 1.45),
            ("Brass Padlock Heavy 60mm Keyed Alike", 5, 7.40, 5.20),
            ("Heavy Door Closer Commercial Grade 1", 5, 32.00, 23.00),
            ("Stainless Steel Butt Hinge 4 inch Pair", 5, 5.50, 3.80),
            ("Industrial Sliding Door Gear Track 3m", 5, 48.00, 34.00),
            ("Silicone Sealant High Performance 300ml", 5, 2.60, 1.80),
        ]

        product_objs = []
        for i, (name, cat_idx, price, cost) in enumerate(product_templates, start=1):
            prod = Product(
                name=name,
                category_id=cat_ids[cat_idx],
                sku=f"SKU-{cat_idx+1:02d}-{i:03d}",
                price=price,
                cost=cost,
                active=True,
            )
            session.add(prod)
            product_objs.append(prod)
        session.commit()
        for p in product_objs:
            session.refresh(p)
        product_ids = [p.id for p in product_objs]
        product_prices = {p.id: p.price for p in product_objs}

        print("5. Seeding 60 Customers...")
        customer_names = [
            ("Al-Futtaim Construction Oman", "Commercial"),
            ("Galfar Engineering & Contracting", "Corporate"),
            ("Larsen & Toubro Oman LLC", "Corporate"),
            ("Douglas OHI JV", "Corporate"),
            ("Carillion Alawi Contracting", "Corporate"),
            ("Oman National Transport Co", "Wholesale"),
            ("Hasan Juma Backer Trading", "Corporate"),
            ("Al-Turki Enterprises", "Corporate"),
            ("Oman Shapoorji Construction", "Corporate"),
            ("Al-Adrak Trading & Contracting", "Corporate"),
            ("Bahwan Engineering Group", "Corporate"),
            ("Towell Construction Co", "Corporate"),
            ("Sarooj Construction Company", "Corporate"),
            ("Target LLC Muscat", "Commercial"),
            ("Al-Tasnim Enterprises", "Corporate"),
            ("Oman Ceramics Company", "Wholesale"),
            ("Dhofar Power Infrastructure", "Corporate"),
            ("Salalah Port Logistics", "Corporate"),
            ("Sohar Free Zone Services", "Commercial"),
            ("Nizwa Marble & Granite", "Wholesale"),
            ("Oman Aluminum Rolling Co", "Corporate"),
            ("Majan Mining & Extraction", "Wholesale"),
            ("Oman Fasteners Factory", "Commercial"),
            ("Al-Madina Real Estate Development", "Corporate"),
            ("Barka Water Desalination Co", "Corporate"),
            ("Al-Batinah Poultry Farms", "Commercial"),
            ("Sur Petrochemical Supplies", "Corporate"),
            ("Buraimi Trading & Contracting", "Commercial"),
            ("Khimji Ramdas Infrastructure", "Corporate"),
            ("Shanfari Group Construction", "Corporate"),
            ("WJ Towell Building Dept", "Corporate"),
            ("Zubair Automotive Works", "Wholesale"),
            ("Muscat Municipality Maintenance", "Government"),
            ("Ministry of Transport Projects", "Government"),
            ("Royal Oman Police Facilities", "Government"),
            ("Oman Cables Industry SAOG", "Corporate"),
            ("Oman Steel Wire LLC", "Commercial"),
            ("Al-Hail Electro-Mechanical", "Commercial"),
            ("Qurum Heights Interior", "Retail"),
            ("Bausher Maintenance Contracting", "Retail"),
            ("Azaiba Technical Services", "Retail"),
            ("Seeb Industrial Workshop", "Retail"),
            ("Mabela Heavy Equipment Spares", "Retail"),
            ("Ruwi Electrical Traders", "Retail"),
            ("Ghala Logistics Warehouse", "Commercial"),
            ("Salalah Beach Resort Dev", "Commercial"),
            ("Taqah Engineering Works", "Retail"),
            ("Sohar Metal Craft", "Commercial"),
            ("Liwa Trading Establishment", "Retail"),
            ("Nizwa Fort Restoration Co", "Commercial"),
            ("Bahla Pottery & Tile Factory", "Commercial"),
            ("Ibri Quarry Operations", "Wholesale"),
            ("Rustaq Agricultural Projects", "Commercial"),
            ("Al-Khaburah Fisheries Marine", "Commercial"),
            ("Musandam Marine Services", "Commercial"),
            ("Duqm Port Heavy Maintenance", "Corporate"),
            ("Al-Wusta Desert Contractors", "Commercial"),
            ("Mirbat Coastal Developments", "Commercial"),
            ("Adam Airbase Logistics", "Government"),
            ("Sinaw Livestock Market Facility", "Commercial"),
        ]

        customer_objs = []
        for i, (name, ctype) in enumerate(customer_names, start=1):
            assigned_branch = branch_ids[(i - 1) % len(branch_ids)]
            cust = Customer(
                name=name,
                email=f"procurement@{name.lower().replace(' ', '').replace('&', '').replace('/', '')[:15]}.om",
                branch_id=assigned_branch,
                customer_type=ctype,
                created_at=datetime(2024, 1, 1, tzinfo=timezone.utc) + timedelta(days=i * 5),
            )
            session.add(cust)
            customer_objs.append(cust)
        session.commit()
        for c in customer_objs:
            session.refresh(c)
        customer_ids = [c.id for c in customer_objs]

        print("6. Seeding 25 Suppliers...")
        suppliers_data = [
            ("Jindal Shadeed Iron & Steel", "Rajesh Sharma", "Sohar"),
            ("Oman Cables Industry SAOG", "Ahmed Al-Siyabi", "Rusayl"),
            ("Oman Cement Company", "Said Al-Rawahi", "Rusayl"),
            ("Raysut Cement Company", "Salim Al-Shanfari", "Salalah"),
            ("Ducab Cables Oman", "Tariq Mansoor", "Muscat"),
            ("Amiantit Oman Pipes", "Kamal Ibrahim", "Rusayl"),
            ("Voltamp Transformers Oman", "Mohammed Al-Harthy", "Sohar"),
            ("Oman Fiber Optic Co", "Khalid Al-Balushi", "Rusayl"),
            ("Schneider Electric Oman", "Pierre Dubois", "Muscat"),
            ("ABB Oman LLC", "Hans Meyer", "Muscat"),
            ("Siemens Middle East Oman", "Marco Rossi", "Muscat"),
            ("National Heaters Industries", "Faisal Al-Kindi", "Rusayl"),
            ("Gulf Plastic Industries", "Hassan Al-Zadjali", "Sohar"),
            ("Oman Fasteners LLC", "Nasser Al-Mashani", "Sohar"),
            ("Bahwan Building Materials", "P. Nair", "Muscat"),
            ("Al-Saleh Trading Muscat", "Ali Al-Saleh", "Muscat"),
            ("Middle East Pipe Solutions", "Adel Al-Ghafri", "Sohar"),
            ("Oman Safety & Security Equipment", "Omar Al-Habsi", "Muscat"),
            ("Pact Engineering Tools", "Suresh Kumar", "Muscat"),
            ("Salalah Free Zone Supplies", "Muna Al-Kathiri", "Salalah"),
            ("Dhofar Industrial Gases", "Abdullah Bait Ali", "Salalah"),
            ("Al-Batinah International Tools", "Hamad Al-Busaidi", "Sohar"),
            ("Oman National Fasteners", "Rashid Al-Kiyumi", "Nizwa"),
            ("Dakhiliyah Heavy Equipment", "Khalfan Al-Abri", "Nizwa"),
            ("Al-Jazeera Steel Products", "Venkatesh Rao", "Sohar"),
        ]
        supplier_objs = []
        for name, contact, city in suppliers_data:
            supp = Supplier(name=name, contact=contact, city=city)
            session.add(supp)
            supplier_objs.append(supp)
        session.commit()
        for s in supplier_objs:
            session.refresh(s)
        supplier_ids = [s.id for s in supplier_objs]

        print("7. Seeding Inventory (Branches x Products)...")
        inventory_records = []
        for b_id in branch_ids:
            for p_id in product_ids:
                qty = random.randint(15, 350)
                reorder = random.randint(10, 40)
                inventory_records.append({
                    "branch_id": b_id,
                    "product_id": p_id,
                    "quantity": qty,
                    "reorder_level": reorder,
                    "updated_at": datetime.now(timezone.utc),
                })
        session.bulk_insert_mappings(Inventory, inventory_records)
        session.commit()

        print("8. Seeding Purchases...")
        purchases_records = []
        start_date = date(2024, 1, 1)
        end_date = date(2026, 9, 28)
        total_days = (end_date - start_date).days

        for i in range(1, 1201):
            p_date = start_date + timedelta(days=random.randint(0, total_days))
            supp_id = random.choice(supplier_ids)
            b_id = random.choice(branch_ids)
            tot = round(random.uniform(1500.0, 45000.0), 2)
            purchases_records.append({
                "supplier_id": supp_id,
                "branch_id": b_id,
                "purchase_date": p_date,
                "total_amount": tot,
                "status": random.choice(["Completed", "Completed", "Completed", "Pending"]),
            })
        session.bulk_insert_mappings(Purchase, purchases_records)
        session.commit()

        print(f"9. Seeding {num_sales} Sales and Sale Items (deterministic batching)...")
        # Generate sales deterministically across 2024-01-01 to 2026-09-28
        # Ensure higher volume for Muscat, then Sohar, Salalah, Nizwa
        branch_weights = [0.45, 0.22, 0.20, 0.13]  # Muscat, Salalah, Sohar, Nizwa
        sale_batch_size = 5000
        
        # Precompute date distribution to ensure rich current month (September 2026) data
        current_year = 2026
        current_month = 9
        
        sales_to_insert = []
        items_to_insert = []
        
        invoice_counter = 100000
        
        for i in range(num_sales):
            invoice_counter += 1
            inv_no = f"INV-2026-{invoice_counter}"
            
            # 20% in last 3 months, 10% in current month, 70% in rest of 2024-2026
            r = random.random()
            if r < 0.12:
                # Current month: 2026-09-01 to 2026-09-28
                s_date = date(2026, 9, random.randint(1, 28))
            elif r < 0.35:
                # Last 3 months: July, August, September 2026
                m = random.choice([7, 8])
                s_date = date(2026, m, random.randint(1, 28))
            else:
                # Anywhere from 2024-01-01 to 2026-06-30
                d_offset = random.randint(0, 900)
                s_date = start_date + timedelta(days=d_offset)
                if s_date > end_date:
                    s_date = end_date
            
            # Select branch with weights
            b_id = random.choices(branch_ids, weights=branch_weights, k=1)[0]
            # Select customer
            c_id = random.choice(customer_ids)
            
            # Generate 1 to 4 items
            num_items = random.choices([1, 2, 3, 4], weights=[0.45, 0.35, 0.15, 0.05], k=1)[0]
            chosen_prods = random.sample(product_ids, k=num_items)
            
            sale_gross = 0.0
            sale_items = []
            for p_id in chosen_prods:
                u_price = product_prices[p_id]
                qty = random.choices([1, 2, 5, 10, 20, 50, 100], weights=[0.35, 0.25, 0.15, 0.12, 0.08, 0.03, 0.02], k=1)[0]
                item_tot = round(qty * u_price, 2)
                sale_gross += item_tot
                sale_items.append((p_id, qty, u_price, item_tot))
            
            discount = round(sale_gross * (0.05 if sale_gross > 500 else 0.0), 2)
            tax = round((sale_gross - discount) * 0.05, 2)  # 5% Oman VAT
            net_amt = round((sale_gross - discount) + tax, 2)
            
            sales_to_insert.append({
                "id": i + 1,
                "invoice_number": inv_no,
                "customer_id": c_id,
                "branch_id": b_id,
                "sale_date": s_date,
                "gross_amount": round(sale_gross, 2),
                "discount": discount,
                "tax": tax,
                "net_amount": net_amt,
                "status": "Completed" if random.random() > 0.03 else "Cancelled",
            })
            
            for (p_id, qty, u_price, item_tot) in sale_items:
                items_to_insert.append({
                    "sale_id": i + 1,
                    "product_id": p_id,
                    "quantity": qty,
                    "unit_price": u_price,
                    "discount": 0.0,
                    "total_amount": item_tot,
                })
            
            if len(sales_to_insert) >= sale_batch_size:
                session.bulk_insert_mappings(Sale, sales_to_insert)
                session.bulk_insert_mappings(SaleItem, items_to_insert)
                session.commit()
                sales_to_insert.clear()
                items_to_insert.clear()
                print(f"   ...seeded {i+1}/{num_sales} sales")

        if sales_to_insert:
            session.bulk_insert_mappings(Sale, sales_to_insert)
            session.bulk_insert_mappings(SaleItem, items_to_insert)
            session.commit()
            print(f"   ...seeded {num_sales}/{num_sales} sales")

        print("10. Seeding Sample Audit Log Entries...")
        sample_audits = [
            {
                "user_id": 1,
                "user_role": "Admin",
                "branch_id": None,
                "language": "en",
                "user_question": "Show me total sales by branch for this month",
                "conversation_id": "conv-demo-01",
                "ai_provider": "openai",
                "model": "gpt-4o-mini",
                "generated_sql": "SELECT b.name as branch, SUM(s.net_amount) as total_sales FROM sales s JOIN branches b ON s.branch_id = b.id WHERE s.sale_date >= '2026-09-01' GROUP BY b.name ORDER BY total_sales DESC",
                "validated_sql": "SELECT b.name as branch, SUM(s.net_amount) as total_sales FROM sales s JOIN branches b ON s.branch_id = b.id WHERE s.sale_date >= '2026-09-01' GROUP BY b.name ORDER BY total_sales DESC",
                "execution_time_ms": 14.5,
                "result_row_count": 4,
                "chart_type": "bar",
                "success": True,
                "error_message": None,
                "final_response": "Total sales for September 2026 reached 428,500 OMR across all branches, led by Muscat branch.",
                "token_count": 312,
            },
            {
                "user_id": 2,
                "user_role": "Branch Manager",
                "branch_id": muscat_id,
                "language": "ar",
                "user_question": "ما هي المبيعات حسب الفرع هذا الشهر؟",
                "conversation_id": "conv-demo-02",
                "ai_provider": "openai",
                "model": "gpt-4o-mini",
                "generated_sql": f"SELECT b.name as branch, SUM(s.net_amount) as total_sales FROM sales s JOIN branches b ON s.branch_id = b.id WHERE s.branch_id = {muscat_id} AND s.sale_date >= '2026-09-01' GROUP BY b.name",
                "validated_sql": f"SELECT b.name as branch, SUM(s.net_amount) as total_sales FROM sales s JOIN branches b ON s.branch_id = b.id WHERE s.branch_id = {muscat_id} AND s.sale_date >= '2026-09-01' GROUP BY b.name",
                "execution_time_ms": 8.2,
                "result_row_count": 1,
                "chart_type": "bar",
                "success": True,
                "error_message": None,
                "final_response": "بلغ إجمالي مبيعات فرع مسقط لشهر سبتمبر 2026 ما مقداره 208,300 ر.ع. ضمن الصلاحية المحددة للفرع.",
                "token_count": 285,
            }
        ]
        for a in sample_audits:
            session.add(AuditLog(**a))
        session.commit()

        # Synchronize sequences on PostgreSQL
        if engine.dialect.name == "postgresql":
            from sqlalchemy import text
            print("Synchronizing PostgreSQL sequences...")
            for table_name in ["branches", "users", "categories", "products", "customers", "suppliers", "purchases", "sales", "sale_items", "inventory", "audit_logs"]:
                try:
                    session.execute(text(f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), coalesce(max(id), 1)) FROM {table_name};"))
                    session.commit()
                except Exception:
                    session.rollback()

        print("\n=== SUCCESS: Database seeded successfully! ===")
        print(f"Branches: {len(branch_objs)}")
        print(f"Products: {len(product_objs)}")
        print(f"Customers: {len(customer_objs)}")
        print(f"Suppliers: {len(supplier_objs)}")
        print(f"Sales Records: {num_sales}")
        print("Demo Users:")
        print(" - Admin: admin@mmi-demo.com (Demo@12345)")
        print(" - Branch Manager: manager@mmi-demo.com (Demo@12345, Muscat)")
        print(" - Analyst: analyst@mmi-demo.com (Demo@12345)")

    except Exception as e:
        session.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    seed_database(num_sales=50000)
