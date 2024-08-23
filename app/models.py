from sqlalchemy import Column, Integer, String,Date,Boolean, ForeignKey,ForeignKeyConstraint,Float
from database import Base

# This is the file for defining classes for the ORM
class Customer(Base):
    __tablename__ = 'Customer'
    Ssn = Column(String(9),primary_key=True)
    CustName = Column(String(50))
    Address=Column(String(100))
    HealthDetails_num = Column(Integer)
 
    def __init__(self, Ssn, CustName,Address,HealthDetails_num):
        self.Ssn=Ssn
        self.CustName=CustName
        self.Address=Address
        self.HealthDetails_num=HealthDetails_num
        # self.HealthInfo=HealthInfo
    
class ContractBenefit(Base):
    __tablename__='ContractBenefit'
    Contract_num=Column(String(10))
    Beneficiary_ssn = Column(String(9))
    Benefit_num = Column(String(10))
    ContractBenefit_num = Column(String(10),primary_key=True)
    Premium = Column(Float)
    def __init__(self,Contract_num,Beneficiary_ssn,Benefit_num,ContractBenefit_num,Premium):
        self.Contract_num=Contract_num
        self.Beneficiary_ssn = Beneficiary_ssn
        self.Benefit_num = Benefit_num
        self.ContractBenefit_num = ContractBenefit_num
        self.Premium=Premium

class BillingAccount(Base):
    __tablename__='BillingAccount'
    BillingAccount_name=Column(String(50))
    Group_num=Column(String(10))
    BillingAddress=Column(String(1000))
    BillingAccount_num=Column(String(10),primary_key=True)
    def __init__(self, BillingAccount_name,Group_num,BillingAddress,BillingAccount_num):
        self.BillingAccount_name=BillingAccount_name
        self.Group_num=Group_num
        self.BillingAddress=BillingAddress
        self.BillingAccount_num=BillingAccount_num
class Associate(Base):
    __tablename__='Associate'
    Associate_name=Column(String(50))
    Id = Column(String(10),primary_key=True)
    Address=Column(String(100))
    Earnings=Column(Float)
    def __init__(self,Associate_name,Id,Tenure_date,Address,Earnings):
        self.Associate_name = Associate_name
        self.Id = Id
        self.Tenure_date=Tenure_date
        self.Address=Address
        self.Earnings=Earnings
class Contract(Base):
    __tablename__='Contract'
    Contract_details = Column(String(500))
    Contract_num = Column(String(10),primary_key=True)
    def __init__(self, Contract_details, Contract_num):
        self.Contract_details=Contract_details
        self.Contract_num=Contract_num
class Claim(Base):
    __tablename__="Claim"
    Claim_num=Column(String(10),primary_key=True)
    Claim_date=Column(Date)
    Participant_ssn=Column(String(9),ForeignKey("Customer.Ssn"))
    ContractBenefit_num=Column(String(10),ForeignKey("ContractBenefit.ContractBenefit_num"))
    BillingAccount_num = Column(String(10), ForeignKey("BillingAccount.BillingAccount_num"))
    Description=Column(String(200))
    def __init__(self,Claim_num,Claim_date,Participant_ssn,ContractBenefit_num,BillingAccount_num,Description):
        self.Claim_num=Claim_num
        self.Claim_date=Claim_date
        self.Participant_ssn=Participant_ssn
        self.ContractBenefit_num=ContractBenefit_num
        self.BillingAccount_num=BillingAccount_num
        self.Description=Description
class Remittance(Base):
    __tablename__="Remittance"
    GivenDate=Column(Date)
    Dollar_amount=Column(Integer)
    Remittance_num=Column(String(10),primary_key=True)
    BillingAccount_num=Column(String(10),ForeignKey("BillingAccount.BillingAccount_num"))
    ContractBenefit_num=Column(String(10),ForeignKey("BillingAccount.ContractBenefit_num"))
    Claim_num=Column(String(10),ForeignKey("Claim.Claim_num"))
    def __init__(self,GivenDate,Dollar_amount, Remittance_num,BillingAccount_num,Claim_num,ContractBenefit_num) -> None:
        self.GivenDate=GivenDate
        self.Dollar_amount=Dollar_amount
        self.Remittance_num=Remittance_num
        self.BillingAccount_num=BillingAccount_num
        self.Claim_num=Claim_num
        self.ContractBenefit_num=ContractBenefit_num

class Invoice(Base):
    __tablename__="Invoice"
    Invoice_num=Column(String(10),primary_key=True)
    File_date=Column(Date)
    Dollar_amount=Column(Integer)
    ContractBenefit_num=Column(String(10))
    BillingAccount_num=Column(String(10))
    def __init__(self,Invoice_num,File_date,Dollar_amount,
                 ContractBenefit_num,BillingAccount_num):
        self.Invoice_num=Invoice_num
        self.File_date=File_date
        self.Dollar_amount=Dollar_amount
        self.ContractBenefit_num=ContractBenefit_num
        self.BillingAccount_num=BillingAccount_num
class BequeathMoneyTo(Base):
    __tablename__="BequeathMoneyTo"
    AssociateId=Column(String(10),ForeignKey("Associate.Id"),primary_key=True)
    CustomerSsn=Column(String(10),ForeignKey("Customer.Ssn"),primary_key=True)
    Percent=Column(Float)
    def __init__(self,AssociateId,CustomerSsn,Percent):
        self.AssociateId=AssociateId
        self.CustomerSsn=CustomerSsn
        self.Percent=Percent

class HeartDisease(Base):
    __tablename__="HeartDisease"
    Smoking=Column(Boolean)
    AlcoholDrinking=Column(Boolean)
    Stroke=Column(Boolean)
    Sex=Column(Boolean)
    Asthma=Column(Boolean)
    normalized_BMI=Column(Float)
    normalized_Age=Column(Float)
    HealthDetails_num=Column(Integer,primary_key=True)

class Diabetes(Base):
    __tablename__="Diabetes"
    gender=Column(Boolean)
    normalized_age=Column(Float)
    hypertension=Column(Boolean)
    heart_disease=Column(Boolean)
    normalized_bmi=Column(Float)
    HealthDetails_num=Column(Integer,primary_key=True)

class Stroke(Base):
    __tablename__="Stroke"
    gender=Column(Boolean)
    normalized_age=Column(Float)
    hypertension=Column(Boolean)
    heart_disease=Column(Boolean)
    normalized_bmi=Column(Float)
    normalized_avg_glucose_level=Column(Float)
    ever_smoked=Column(Boolean)
    current_smoker=Column(Boolean)
    HealthDetails_num=Column(Integer,primary_key=True)

class Alzheimers(Base):
    __tablename__="Alzheimers"
    normalized_Age=Column(Integer)
    normalized_SystolicBP=Column(Integer)
    normalized_DiastolicBP=Column(Integer)
    normalized_CholesterolTotal=Column(Integer)
    HealthDetails_num=Column(Integer,primary_key=True)

class ProductionCredit(Base):
    __tablename__="ProductionCredit"
    ContractBenefit_num=Column(String(10),ForeignKey("ContractBenefit.ContractBenefit_num"),primary_key=True)
    Sitcode=Column(String(10),ForeignKey("ManagerContract.Sitcode"),primary_key=True)
    Percentage=Column(Float)

class Commission(Base):
    __tablename__="Commission"
    ContractBenefit_num=Column(String(10),ForeignKey("ContractBenefit.ContractBenefit_num"),primary_key=True)
    Sitcode=Column(String(10),ForeignKey("ManagerContract.Sitcode"),primary_key=True)
    Percentage=Column(Float)
class ManagerContract(Base):
    __tablename__="ManagerContract"
    Sitcode=Column(String(10),primary_key=True)
    Start_date=Column(Date)
    Issue_date=Column(Date)
    AssociateId = Column(String(10),ForeignKey("Associate.Id"))
    District=Column(String(50))