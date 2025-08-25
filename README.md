# Database Systems Final Project
This is the final project for my Database Systems course.

It is a flask app using mysql-alchemy ORM and scikitlearn for a machine learning model. It models a health insurance company, with different users, policies, and health data. 
The cost for the policies are determined by a user's health data. 

**Physical Database Design:**

All primary keys become primary indices for their table (ie, the rows are clustered by their primary key value). All foreign keys become secondary indices for their table. In addition, all dates become indices to allow users to more easily select by date. The files are clustered by their primary index and all use the B+ tree data structure since this is the only one supported by the table's storage engine. This is seen in the project_schema folder.
 
Here is a non-comprehensive list of business use-cases for these indices:

-	A customer wants to see if the insurance gave them a refund. The system finds the ContractBenefit for which they are the beneficiary using the index Beneficiary_Ssn, to find the corresponding ContractBenefit#. The system can then select from the table Remittance with the customer's specified ContractBenefit#, an index of the table, and then view them in chronological order by Remittance's index given_date index to see the recent ones. Alternatively, the customer can see the claims for a given claim by selecting on the index Claim#.
-	A customer wants to see how much they owe. The system finds the ContractBenefit for which they are the beneficiary using the index Beneficiary_Ssn, to find the corresponding ContractBenefit#. The system can then select from the table Invoice with the customer's specified ContractBenefit#, an index of the table, and then view them in chronological order by Invoice's index given_date index to see the recent ones. 
-	The company wants to process recent claims. They take the information out of the Claim table, sorted by the index File_date.
-	An associate dies and the company wants to bequeath their earnings. So the system looks at the BequeathMoneyTo table and select by the index AssociateId to find the customers that the associate bequeaths to. They can then select into the table Customer for that Ssn value and send a check to the address on file for the customer.
-	The customer pays their premium and all relevant associates need to receive a cut. he system finds the ContractBenefit for which they are the beneficiary using the index Beneficiary_Ssn, to find the corresponding ContractBenefit#. The system then selects from the Commission table on the ContractBenefit# index to find all AssociateIDs, then finds that Associate in the Associated table using the AssociateID index, and then mails a check to the address written there.
 
**Machine learning model:**

You can find my machine learning models in machine_learning.ipynb. My machine learning models would be deployed to predict each customer’s chance of developing various diseases based on their health date. In the first cell you see an example of the visualization capabilities. It is the result of a regression on age with the probability of developing diseases. As you can see, the older someone is, the likelier they are to have diabetes. 
Each next cell deals with a different dataset, 4 total: diabetes, heart disease, stroke, and alzheimer’s. Each machine learning model learns to predict the probability that a patient has the disease based on their health attributes. They all use logistic regression as the most appropriate tool for this type of prediction.
Finally, in the last cell there is a function that can take any model, a cost for the disease, and a markup, and calculate the premium that that customer should pay for that disease.
