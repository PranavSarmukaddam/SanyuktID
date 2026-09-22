from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(DB_DIR, "sanyukt.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="citizen")  # citizen | officer | admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    citizen = relationship("Citizen", back_populates="user", uselist=False)
    officer = relationship("Officer", back_populates="user", uselist=False)


class Citizen(Base):
    __tablename__ = "citizens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    sanyukt_id = Column(String(30), unique=True, index=True)
    full_name = Column(String(200))
    aadhaar_last4 = Column(String(4))
    mobile = Column(String(15))
    email = Column(String(200))
    address = Column(Text)
    district = Column(String(100))
    dob = Column(String(20))
    gender = Column(String(10))
    user = relationship("User", back_populates="citizen")
    applications = relationship("Application", back_populates="citizen")
    consents = relationship("Consent", back_populates="citizen")
    notifications = relationship("Notification", back_populates="citizen")


class Officer(Base):
    __tablename__ = "officers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    officer_id = Column(String(50), unique=True)
    full_name = Column(String(200))
    department = Column(String(100))
    designation = Column(String(100))
    user = relationship("User", back_populates="officer")


class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True)
    name = Column(String(200))
    api_base_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    failure_mode = Column(Boolean, default=False)  # toggle to simulate failure
    services = relationship("Service", back_populates="department")


class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"))
    code = Column(String(50), unique=True)
    name = Column(String(200))
    description = Column(Text)
    required_departments = Column(Text)  # comma-separated department codes
    department = relationship("Department", back_populates="services")


class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(String(50), unique=True, index=True)
    citizen_id = Column(Integer, ForeignKey("citizens.id"))
    service_id = Column(Integer, ForeignKey("services.id"))
    status = Column(String(50), default="SUBMITTED")  # SUBMITTED|IN_PROGRESS|COMPLETED|FAILED|ON_HOLD
    current_step = Column(Integer, default=0)
    form_data = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    citizen = relationship("Citizen", back_populates="applications")
    service = relationship("Service")
    steps = relationship("ApplicationStep", back_populates="application", order_by="ApplicationStep.step_number")


class ApplicationStep(Base):
    __tablename__ = "application_steps"
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"))
    step_number = Column(Integer)
    step_name = Column(String(200))
    department = Column(String(100))
    status = Column(String(50), default="PENDING")  # PENDING|IN_PROGRESS|COMPLETED|FAILED
    result_data = Column(JSON, default={})
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    application = relationship("Application", back_populates="steps")


class Consent(Base):
    __tablename__ = "consents"
    id = Column(Integer, primary_key=True, index=True)
    citizen_id = Column(Integer, ForeignKey("citizens.id"))
    application_id = Column(String(50), nullable=True)
    department_code = Column(String(50))
    data_types = Column(Text)  # comma-separated
    granted = Column(Boolean, default=True)
    granted_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    citizen = relationship("Citizen", back_populates="consents")


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    citizen_id = Column(Integer, ForeignKey("citizens.id"))
    application_id = Column(String(50), nullable=True)
    title = Column(String(300))
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    citizen = relationship("Citizen", back_populates="notifications")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_identifier = Column(String(200))
    system = Column(String(100))
    action = Column(String(300))
    application_id = Column(String(50), nullable=True)
    status = Column(String(50))
    details = Column(JSON, default={})


class ApiLog(Base):
    __tablename__ = "api_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    source_system = Column(String(100))
    target_system = Column(String(100))
    endpoint = Column(String(300))
    method = Column(String(10))
    request_data = Column(JSON, default={})
    response_data = Column(JSON, default={})
    status_code = Column(Integer)
    duration_ms = Column(Integer)
    application_id = Column(String(50), nullable=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)


def seed_data():
    import bcrypt
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(User).first():
            return

        # Departments (8 Major Maharashtra State Departments)
        revenue = Department(code="REVENUE", name="Revenue & Forest Department (महसूल व वन विभाग)", api_base_url="http://localhost:8001", failure_mode=False)
        municipal = Department(code="MUNICIPAL", name="Urban Development & Municipal Administration (नगर विकास विभाग)", api_base_url="http://localhost:8002", failure_mode=False)
        welfare = Department(code="WELFARE", name="Social Justice & Special Assistance (सामाजिक न्याय विभाग)", api_base_url="http://localhost:8003", failure_mode=False)
        rural = Department(code="RURAL", name="Rural Development & Panchayati Raj (ग्राम विकास विभाग)", api_base_url="http://localhost:8004", failure_mode=False)
        health = Department(code="HEALTH", name="Public Health & Family Welfare (सार्वजनिक आरोग्य विभाग)", api_base_url="http://localhost:8005", failure_mode=False)
        agri = Department(code="AGRICULTURE", name="Agriculture & Farmers Welfare (कृषी विभाग)", api_base_url="http://localhost:8006", failure_mode=False)
        labour = Department(code="LABOUR", name="Labour & Employment Department (कामगार विभाग)", api_base_url="http://localhost:8007", failure_mode=False)
        higher_ed = Department(code="HIGHER_ED", name="Higher & Technical Education (उच्च व तंत्र शिक्षण विभाग)", api_base_url="http://localhost:8008", failure_mode=False)
        
        db.add_all([revenue, municipal, welfare, rural, health, agri, labour, higher_ed])
        db.flush()

        # Services Catalog (24+ Key Citizen Services)
        services = [
            # Revenue Services
            Service(department_id=revenue.id, code="PROP_TRANSFER", name="Property Transfer & Mutation (Ferfar)", description="Integrated ownership transfer and online Ferfar entry across revenue and urban registries.", required_departments="REVENUE,MUNICIPAL"),
            Service(department_id=revenue.id, code="PROP_CERT", name="Digitally Signed 7/12 & 8A Extract", description="Official digitally signed Land Record extract with RoR status and survey verification.", required_departments="REVENUE"),
            Service(department_id=revenue.id, code="INCOME_CERT", name="Tahasildar Income Certificate", description="Certified certificate of annual income issued by Revenue Authorities for state schemes.", required_departments="REVENUE"),
            Service(department_id=revenue.id, code="DOMICILE_CERT", name="Age, Nationality & Domicile Certificate", description="Official Maharashtra state domicile and residential entitlement certificate.", required_departments="REVENUE"),
            Service(department_id=revenue.id, code="CASTE_CERT", name="Caste Certificate & Scrutiny", description="Caste certificate issuance with automated backward class registry verification.", required_departments="REVENUE,WELFARE"),
            Service(department_id=revenue.id, code="NON_CREAMY", name="Non-Creamy Layer Certificate", description="Certificate for eligible categories based on 3-year verified IT / agricultural revenue data.", required_departments="REVENUE"),

            # Municipal Services
            Service(department_id=municipal.id, code="BLDG_PERMISSION", name="Integrated Building Plan Approval (BPAMS)", description="Single-window building permit clearance, zone classification, and structural NOC.", required_departments="MUNICIPAL,REVENUE"),
            Service(department_id=municipal.id, code="WATER_CONN", name="New Water & Drainage Connection", description="Application for tap water connection and drainage line integration from local body.", required_departments="MUNICIPAL"),
            Service(department_id=municipal.id, code="BIRTH_CERT", name="Birth / Death Certificate", description="Civil registration extract and certified copies issued by Municipal / Nagar Parishad.", required_departments="MUNICIPAL"),
            Service(department_id=municipal.id, code="TRADE_LICENSE", name="Municipal Trade License & Renewal", description="Business commercial establishment license issued by Municipal Corporation.", required_departments="MUNICIPAL"),
            Service(department_id=municipal.id, code="PROP_TAX", name="Property Tax Assessment Extract", description="Certified assessment of annual ratable value (ARV) and tax payment clearance NOC.", required_departments="MUNICIPAL"),

            # Social Welfare Services
            Service(department_id=welfare.id, code="SCHOLARSHIP", name="Post-Matric Education Scholarship (MahaDBT)", description="Tuition fees and maintenance allowance for post-matric higher education students.", required_departments="WELFARE,REVENUE,HIGHER_ED"),
            Service(department_id=welfare.id, code="WELFARE_SCHEME", name="Sanjay Gandhi Niradhar Anudan Yojana", description="Financial assistance to destitute persons, disabled, and widows below poverty threshold.", required_departments="WELFARE,REVENUE"),
            Service(department_id=welfare.id, code="FIN_ASSISTANCE", name="Shravanbal Seva State Pension", description="Monthly old-age pension for senior citizens aged 65 years and above in Maharashtra.", required_departments="WELFARE,REVENUE"),
            Service(department_id=welfare.id, code="DIVYANG_AID", name="Divyangjan Assistive Equipment Subsidy", description="State grant for specialized medical and mobility aids for differently-abled citizens.", required_departments="WELFARE"),

            # Rural Development Services
            Service(department_id=rural.id, code="GRAM_NOC", name="Gram Panchayat Namuna 8 Property Extract", description="House tax and property ownership record verification for rural village jurisdictions.", required_departments="RURAL,REVENUE"),
            Service(department_id=rural.id, code="RURAL_WATER", name="Rural Water Supply (Jal Jeevan Mission)", description="Household tap connection clearance under Zilla Parishad water scheme.", required_departments="RURAL"),

            # Public Health Services
            Service(department_id=health.id, code="HEALTH_CARD", name="Mahatma Jyotirao Phule Jan Arogya Card", description="Universal health insurance coverage up to ₹5 Lakhs for specialized hospitalization.", required_departments="HEALTH,REVENUE"),
            Service(department_id=health.id, code="FOOD_SAFETY", name="Food Business Registration (FDA)", description="Hygiene and food establishment clearance under state public health safety norms.", required_departments="HEALTH"),

            # Agriculture Services
            Service(department_id=agri.id, code="KRISHI_SUBSIDY", name="Farm Mechanization Subsidy (MahaDBT Krishi)", description="State capital subsidy for purchase of tractors, rotavators, and precision drip irrigation.", required_departments="AGRICULTURE,REVENUE"),
            Service(department_id=agri.id, code="SOIL_HEALTH", name="Soil Health Card & Nutrient Advisories", description="Agricultural soil chemical profile test and subsidized fertilizer allocation.", required_departments="AGRICULTURE"),

            # Labour Services
            Service(department_id=labour.id, code="BOCW_REG", name="Building & Construction Worker Registration", description="Welfare board identity smart card and statutory insurance for construction workers.", required_departments="LABOUR"),
            Service(department_id=labour.id, code="SHOP_EST", name="Shop & Commercial Registration (Gumasta)", description="Establishment registration under Maharashtra Shops & Commercial Establishments Act.", required_departments="LABOUR,MUNICIPAL"),

            # Higher Education Services
            Service(department_id=higher_ed.id, code="FEES_CONCESSION", name="Chhatrapati Shahu Maharaj Fee Concession", description="50% tuition and examination fee concession for EBC and SEBC students in professional courses.", required_departments="HIGHER_ED,REVENUE"),
        ]
        db.add_all(services)

        # Citizen user
        citizen_pwd = bcrypt.hashpw(b"citizen123", bcrypt.gensalt()).decode("utf-8")
        citizen_user = User(username="9876543210", hashed_password=citizen_pwd, role="citizen")
        db.add(citizen_user)
        db.flush()
        citizen = Citizen(
            user_id=citizen_user.id,
            sanyukt_id="MH-SYN-2026-000123",
            full_name="Rajesh Kumar Sharma",
            aadhaar_last4="4521",
            mobile="9876543210",
            email="rajesh.sharma@example.com",
            address="B-204, Shivaji Nagar, Pune",
            district="Pune",
            dob="1985-06-15",
            gender="Male"
        )
        db.add(citizen)

        # Officer user
        officer_pwd = bcrypt.hashpw(b"officer123", bcrypt.gensalt()).decode("utf-8")
        officer_user = User(username="OFFICER001", hashed_password=officer_pwd, role="officer")
        db.add(officer_user)
        db.flush()
        officer = Officer(
            user_id=officer_user.id,
            officer_id="OFFICER001",
            full_name="Priya Mehta",
            department="Revenue Department",
            designation="Deputy Collector"
        )
        db.add(officer)
        db.flush()

        # Sample applications
        db.flush()
        citizen_obj = db.query(Citizen).filter_by(user_id=citizen_user.id).first()
        prop_svc = db.query(Service).filter_by(code="PROP_TRANSFER").first()
        bldg_svc = db.query(Service).filter_by(code="BLDG_PERMISSION").first()
        income_svc = db.query(Service).filter_by(code="INCOME_CERT").first()

        app1 = Application(
            application_id="SYN-2026-001",
            citizen_id=citizen_obj.id,
            service_id=prop_svc.id,
            status="IN_PROGRESS",
            current_step=2,
            form_data={"property_id": "PROP-10291", "buyer_name": "Amit Verma", "sale_value": "4500000"}
        )
        db.add(app1)
        db.flush()
        steps1 = [
            ApplicationStep(application_id=app1.id, step_number=1, step_name="Identity Verification", department="SANYUKT", status="COMPLETED", result_data={"verified": True}, completed_at=datetime.utcnow()),
            ApplicationStep(application_id=app1.id, step_number=2, step_name="Revenue Verification", department="REVENUE", status="COMPLETED", result_data={"status": "verified", "property_id": "PROP-10291", "district": "Pune"}, completed_at=datetime.utcnow()),
            ApplicationStep(application_id=app1.id, step_number=3, step_name="Municipal Verification", department="MUNICIPAL", status="IN_PROGRESS", result_data={}, started_at=datetime.utcnow()),
            ApplicationStep(application_id=app1.id, step_number=4, step_name="Revenue Final Approval", department="REVENUE", status="PENDING", result_data={}),
            ApplicationStep(application_id=app1.id, step_number=5, step_name="Citizen Notification", department="SANYUKT", status="PENDING", result_data={}),
        ]
        db.add_all(steps1)

        app2 = Application(
            application_id="SYN-2026-002",
            citizen_id=citizen_obj.id,
            service_id=bldg_svc.id,
            status="SUBMITTED",
            current_step=0,
            form_data={"property_id": "PROP-10291", "building_type": "Residential", "floors": "3"}
        )
        db.add(app2)
        db.flush()
        steps2 = [
            ApplicationStep(application_id=app2.id, step_number=1, step_name="Identity Verification", department="SANYUKT", status="PENDING"),
            ApplicationStep(application_id=app2.id, step_number=2, step_name="Municipal Site Inspection", department="MUNICIPAL", status="PENDING"),
            ApplicationStep(application_id=app2.id, step_number=3, step_name="Revenue NOC", department="REVENUE", status="PENDING"),
            ApplicationStep(application_id=app2.id, step_number=4, step_name="Final Approval", department="MUNICIPAL", status="PENDING"),
        ]
        db.add_all(steps2)

        app3 = Application(
            application_id="SYN-2026-003",
            citizen_id=citizen_obj.id,
            service_id=income_svc.id,
            status="COMPLETED",
            current_step=3,
            form_data={"annual_income": "380000", "occupation": "Private Service"}
        )
        db.add(app3)
        db.flush()
        steps3 = [
            ApplicationStep(application_id=app3.id, step_number=1, step_name="Identity Verification", department="SANYUKT", status="COMPLETED", result_data={"verified": True}, completed_at=datetime.utcnow()),
            ApplicationStep(application_id=app3.id, step_number=2, step_name="Revenue Income Verification", department="REVENUE", status="COMPLETED", result_data={"status": "verified", "income": 380000}, completed_at=datetime.utcnow()),
            ApplicationStep(application_id=app3.id, step_number=3, step_name="Certificate Issue", department="REVENUE", status="COMPLETED", result_data={"certificate_no": "REV-CERT-2026-0089"}, completed_at=datetime.utcnow()),
        ]
        db.add_all(steps3)

        # Consents
        consents = [
            Consent(citizen_id=citizen_obj.id, application_id="SYN-2026-001", department_code="REVENUE", data_types="identity,property", granted=True),
            Consent(citizen_id=citizen_obj.id, application_id="SYN-2026-001", department_code="MUNICIPAL", data_types="identity,property", granted=True),
            Consent(citizen_id=citizen_obj.id, application_id="SYN-2026-003", department_code="REVENUE", data_types="identity,income", granted=True),
        ]
        db.add_all(consents)

        # Notifications
        notifs = [
            Notification(citizen_id=citizen_obj.id, application_id="SYN-2026-001", title="Revenue Verification Completed", message="Revenue Department has successfully verified your property details for application SYN-2026-001.", is_read=False),
            Notification(citizen_id=citizen_obj.id, application_id="SYN-2026-001", title="Application In Progress", message="Your Property Transfer application (SYN-2026-001) is being processed. Municipal verification is underway.", is_read=True),
            Notification(citizen_id=citizen_obj.id, application_id="SYN-2026-003", title="Income Certificate Issued", message="Your Income Certificate has been successfully issued. Certificate Number: REV-CERT-2026-0089.", is_read=False),
            Notification(citizen_id=citizen_obj.id, application_id="SYN-2026-002", title="Application Received", message="Your Building Permission application (SYN-2026-002) has been received and is awaiting processing.", is_read=True),
        ]
        db.add_all(notifs)

        # Audit logs
        logs = [
            AuditLog(user_identifier="Rajesh Kumar Sharma", system="Sanyukt", action="User Login", status="SUCCESS"),
            AuditLog(user_identifier="Rajesh Kumar Sharma", system="Sanyukt", action="Consent Granted — Revenue Dept (SYN-2026-001)", application_id="SYN-2026-001", status="SUCCESS"),
            AuditLog(user_identifier="Rajesh Kumar Sharma", system="Sanyukt", action="Consent Granted — Municipal Dept (SYN-2026-001)", application_id="SYN-2026-001", status="SUCCESS"),
            AuditLog(user_identifier="Sanyukt", system="Revenue API", action="Property Verification — PROP-10291", application_id="SYN-2026-001", status="SUCCESS"),
            AuditLog(user_identifier="Sanyukt", system="Municipal API", action="Property Verification — PROP-10291", application_id="SYN-2026-001", status="SUCCESS"),
            AuditLog(user_identifier="Rajesh Kumar Sharma", system="Sanyukt", action="Application Submitted — Income Certificate", application_id="SYN-2026-003", status="SUCCESS"),
            AuditLog(user_identifier="Sanyukt", system="Revenue API", action="Income Verification", application_id="SYN-2026-003", status="SUCCESS"),
            AuditLog(user_identifier="Sanyukt", system="Revenue API", action="Certificate Issue", application_id="SYN-2026-003", status="SUCCESS"),
        ]
        db.add_all(logs)

        db.commit()
        print("Database seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"Seed error: {e}")
    finally:
        db.close()
