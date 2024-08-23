from flask import Flask, redirect, session,url_for
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import and_,join
from models import *
from flask import request
import datetime
import pandas as pd
from pickle import load
import sklearn


app = Flask(__name__)

from database import init_db
from database import db_session

#intialize the database
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
init_db()

app.secret_key="secret_key" # necessary to get session to work

#this is the home page of the app
@app.route("/")
def index():
    session.clear()
    return render_template("index.html")

#this is the page for customers to enter their Ssn
@app.route("/customer/",methods=["GET","POST"])
def customer():
    val=request.values
    if "Ssn" not in val.keys():
        return render_template("customer/index.html",not_found=False)
     # check that there is such a Ssn in the database:
    query=ContractBenefit.query.filter(ContractBenefit.Beneficiary_ssn==val.get("Ssn"))
    if query.first()==None:
        return render_template("customer/index.html",not_found=True)
    session["Customer_ssn"]=val["Ssn"]
    #enter into the session the numbers of all contractbenefits for which the customer is a beneficiary
    session["ContractBenefit_nums"]=[c.ContractBenefit_num for c in query.all()]
    return redirect("/customer/select")
    
#this is the page for customers to select what use case they want
@app.route("/customer/select")
def customer_select_options():
    return render_template("customer/select.html",claim_filed=False)

#the page for customers to see their remittances
@app.route("/customer/see_remittances")
def customer_see_remittances():
    #get all remittances associated with the customer's contractbenefits
    remittances=Remittance.query.filter(Remittance.ContractBenefit_num.in_(session["ContractBenefit_nums"])).order_by(Remittance.GivenDate.desc()).all()
    remittances=[vars(r) for r in remittances]
    return render_template("customer/see_remittances.html",remittances=remittances)

#the page for customers to see their invoices
@app.route("/customer/see_invoices")
def customer_see_invoices():
    #get all invoices associated with the customer's contractbenefits
    invoices=Invoice.query.filter(Invoice.ContractBenefit_num.in_(session["ContractBenefit_nums"])).order_by(Invoice.File_date.desc()).all()
    invoices=[vars(i) for i in invoices]
    return render_template("customer/see_invoices.html",invoices=invoices)

#the page for customers to file a claim
@app.route("/customer/file_claim")
def customer_file_claim():
    if len(request.values.keys())==0:
        return render_template("customer/file_claim.html")
    
    #check that the entered information (Ssn, BillingAccount number, ContractBenefit number) is valid
    not_found=[]
    if Customer.query.filter(BillingAccount.BillingAccount_num==request.values.get("BillingAccount_num")).first()==None:
        not_found.append("BillingAccount#")
    if Customer.query.filter(ContractBenefit.ContractBenefit_num==request.values.get("ContractBenefit_num")).first()==None:
        not_found.append("ContractBenefit#")

    #if not render the same page
    if not_found!=[]:
        return render_template("customer/file_claim.html",not_found=not_found)
    claim_number=1
    claim_number_str="0"*(10-len(str(claim_number))) + str(claim_number)
    while Customer.query.filter(Claim.Claim_num==claim_number_str).first()!=None:
        claim_number+=1
        claim_number_str="0"*(10-len(str(claim_number))) + str(claim_number)
    current_date=str(datetime.datetime.today()).split()[0]
    created_claim=Claim(claim_number_str,current_date,session["Customer_ssn"],
                        request.values.get("ContractBenefit_num"),
                        request.values.get("BillingAccount_num"),
                        request.values.get("Description"))
    db_session.add(created_claim)
    db_session.commit()
    return render_template("customer/select.html",claim_filed=True)

#the page for business to select use case
@app.route("/business")
def business():
    return render_template("business/index.html",recalculated_premiums=False)

# Method for recalculating premiums
def recalculate_premiums():

    #for alzheimers
    #first: get all entries from the Alzheimers tables that correspond to a customer with Alzheimers benefits
    alzheimers_join=db_session.query(ContractBenefit,Alzheimers).filter(ContractBenefit.Benefit_num=="0000000001")\
        .filter(and_(Customer.Ssn == ContractBenefit.Beneficiary_ssn,Customer.HealthDetails_num==Alzheimers.HealthDetails_num)).all()
    alzheimers_healthdetails=pd.DataFrame([vars(e[2]) for e in alzheimers_join])
    alzheimers_cols=['normalized_Age', 'normalized_SystolicBP', 'normalized_DiastolicBP',
       'normalized_CholesterolTotal']
    alzheimers_healthdetails=alzheimers_healthdetails[alzheimers_cols]
    #next: use the model to calculate premiums for these customers
    with open("../ml_models/alzheimers_model.pkl", "rb") as f:
        alzheimers_model = load(f)
    alzheimers_risks=alzheimers_model.predict_proba(alzheimers_healthdetails)[:,1]
    ALZHEIMERS_COST=1700
    ALZHEIMERS_MARKUP=0.2
    alzheimers_premiums = [ALZHEIMERS_COST*risk*(1+ALZHEIMERS_MARKUP) for risk in alzheimers_risks]
    #finally: update the premiums in the contractbenefit table
    alzheimers_contractbenefits=[e[0] for e in alzheimers_join]
    for i,contractbenefit in enumerate(alzheimers_contractbenefits):
        contractbenefit.Premium = alzheimers_premiums[i]

    #for diabetes
    diabetes_join=db_session.query(ContractBenefit,Diabetes).filter(ContractBenefit.Benefit_num=="0000000002")\
        .filter(and_(ContractBenefit.Benefit_num=="0000000002",and_(Customer.Ssn == ContractBenefit.Beneficiary_ssn,Customer.HealthDetails_num==Diabetes.HealthDetails_num))).all()
    diabetes_healthdetails=pd.DataFrame([vars(e[1]) for e in diabetes_join])
    diabetes_cols=['gender', 'hypertension', 'heart_disease', 'normalized_age','normalized_bmi']    
    diabetes_healthdetails=diabetes_healthdetails[diabetes_cols]
    with open("../ml_models/diabetes_model.pkl", "rb") as f:
        diabetes_model = load(f)
    diabetes_risks=diabetes_model.predict_proba(diabetes_healthdetails)[:,1]
    DIABETES_COST=700
    DIABETES_MARKUP=0.15
    diabetes_premiums = [DIABETES_COST*risk*(1+DIABETES_MARKUP) for risk in diabetes_risks]
    diabetes_contractbenefits=[e[0] for e in diabetes_join]
    for i,contractbenefit in enumerate(diabetes_contractbenefits):
        contractbenefit.Premium = diabetes_premiums[i]

    #for heart disease
    heart_join=db_session.query(ContractBenefit,HeartDisease).filter(ContractBenefit.Benefit_num=="0000000003")\
        .filter(and_(Customer.Ssn == ContractBenefit.Beneficiary_ssn,Customer.HealthDetails_num==HeartDisease.HealthDetails_num)).all()
    heart_healthdetails=pd.DataFrame([vars(e[1]) for e in heart_join])
    heart_cols=['Smoking', 'AlcoholDrinking', 'Stroke', 'Sex', 'Asthma',
       'normalized_BMI', 'normalized_Age']
    heart_healthdetails=heart_healthdetails[heart_cols]
    with open("../ml_models/heart_model.pkl", "rb") as f:
        heart_model = load(f)
    heart_risks=heart_model.predict_proba(heart_healthdetails)[:,1]
    HEART_COST=1000
    HEART_MARKUP=0.2
    heart_premiums = [HEART_COST*risk*(1+HEART_MARKUP) for risk in heart_risks]
    heart_contractbenefits=[e[0] for e in heart_join]
    for i,contractbenefit in enumerate(heart_contractbenefits):
        contractbenefit.Premium = heart_premiums[i]

    #for stroke
    stroke_join=db_session.query(ContractBenefit,Stroke).filter(ContractBenefit.Benefit_num=="0000000004")\
        .filter(and_(Customer.Ssn == ContractBenefit.Beneficiary_ssn,Customer.HealthDetails_num==Stroke.HealthDetails_num)).all()
    stroke_healthdetails=pd.DataFrame([vars(e[1]) for e in stroke_join])
    stroke_cols=['gender', 'hypertension', 'heart_disease','normalized_avg_glucose_level', 'normalized_bmi', 'normalized_age',\
                            'ever_smoked', 'current_smoker']
    stroke_healthdetails=stroke_healthdetails[stroke_cols]
    with open("../ml_models/stroke_model.pkl", "rb") as f:
        stroke_model = load(f)
    stroke_risks=stroke_model.predict_proba(stroke_healthdetails)[:,1]
    STROKE_COST=1000
    STROKE_MARKUP=0.2
    stroke_premiums = [STROKE_COST*risk*(1+STROKE_MARKUP) for risk in stroke_risks]
    stroke_contractbenefits=[e[0] for e in stroke_join]
    for i,contractbenefit in enumerate(stroke_contractbenefits):
        contractbenefit.Premium = stroke_premiums[i]
    db_session.commit()
    
#render this page after the business recalculates premium
@app.route("/business/recalculate_premiums")
def business_recalculated_premiums():
    recalculate_premiums()
    return render_template("business/index.html",recalculated_premiums=True)

#the page for the business to see everyone's premiums 
@app.route("/business/see_premiums")
def business_see_premiums():
    contractbenefits=ContractBenefit.query.all()
    contractbenefits=[vars(c) for c in contractbenefits]
    return render_template("business/see_premiums.html",contractbenefits=contractbenefits)

# the page for the business to see claims in order of recency
@app.route("/business/see_claims")
def business_see_claims():
    claims=Claim.query.order_by(Claim.Claim_date.desc())
    claims=[vars(c) for c in claims]
    return render_template("business/see_claims.html",claims=claims)

#this is the page for the information that a business needs when an employee passes away
@app.route("/business/associate_passed",methods=["GET","POST"])
def business_associate_passed():
    val=request.values
    if len(val)==0:
        return render_template("business/associate_passed.html",not_found=False)
    bequeaths_selected=db_session.query(BequeathMoneyTo,Customer)\
        .filter(and_(BequeathMoneyTo.AssociateId==val.get("Id")),BequeathMoneyTo.CustomerSsn==Customer.Ssn)
    #check if the associate id is not in the bequeath table
    if bequeaths_selected.first()==None:
        return render_template("business/associate_passed.html",not_found=True)
    associate = Associate.query.filter(Associate.Id == val.get("Id")).first()
    customers=[vars(x[0])|vars(x[1]) for x in bequeaths_selected]
    return render_template("business/customers_bequeathed_to.html",customers=customers,associate=vars(associate))

# this is the page for a customer to make a payment
@app.route("/customer/make_payment", methods=["GET","POST"])
def customer_make_payment():
    # check if the form has been submitted
    if len(request.values)==0:
        return render_template("customer/make_payment.html")
    # check if there are no contract benefit numbers
    if ContractBenefit.query.filter(ContractBenefit.ContractBenefit_num==request.values["ContractBenefit_num"]).first()==None:
        return render_template("customer/make_payment.html",not_found=["ContractBenefit#"])


    prod_credits=db_session.query(ProductionCredit,Associate).filter(ProductionCredit.ContractBenefit_num==request.values["ContractBenefit_num"])\
        .filter(and_(ManagerContract.Sitcode==ProductionCredit.Sitcode,Associate.Id==ManagerContract.AssociateId))
    commissions=db_session.query(Commission,Associate).filter(Commission.ContractBenefit_num==request.values["ContractBenefit_num"])\
        .filter(and_(ManagerContract.Sitcode==Commission.Sitcode,Associate.Id==ManagerContract.AssociateId))
    for commission,associate in commissions.all():
        associate.Earnings+=float(request.values["payment"])*commission.Percentage/100
    for prod_credit,associate in prod_credits.all():
        associate.Earnings+=float(request.values["payment"])*prod_credit.Percentage/100
    db_session.commit()
    return render_template("customer/select.html",made_payment=True)