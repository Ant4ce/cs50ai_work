import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4



def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    evidence_lists = []
    labels_list = []

    with open(filename) as csv_file:
        shopping_reader = csv.reader(csv_file)
        row_evidence = []
        int_columns = [0,2,4,11,12,13,14]
        float_colums = [1,3,5,6,7,8,9]
        num = 0
        first_ele = 0
        for row in shopping_reader:
            if first_ele == 0:
                first_ele = 1
                continue
            while num < 17:
                if num in int_columns:
                    row_evidence.append(int(row[num]))
                if num in float_colums:
                    row_evidence.append(float(row[num]))
                if num == 10:
                    row_evidence.append(month_to_num(row[num]))
                    if month_to_num(row[num]) not in [0,1,2,3,4,5,6,7,8,9,10,11]:
                        print("error found in months")
                        break
                if num == 15:
                    row_evidence.append(visit_type(row[num]))
                    if visit_type(row[num]) not in [0,1]:
                        print("error found in visit_type")
                        print(visit_type(row[num]))
                        break
                if num == 16:
                    row_evidence.append(weekend_revenue_num(row[num]))
                    if weekend_revenue_num(row[num]) not in [0,1]:
                        print("error found in weekend_revenue_num")
                        break
                num += 1

            labels_list.append(int(weekend_revenue_num(row[17])))
            evidence_lists.append(row_evidence)
            num = 0
            row_evidence = []


    return evidence_lists, labels_list 


def weekend_revenue_num(number):
    weekend_revenue_state = {"FALSE": 0, "TRUE": 1}
    return weekend_revenue_state.get(number)
    
def month_to_num(month):
    calendar = {"Jan":0, "Feb":1, "Mar":2, "Apr":3, "May":4, "June":5, "Jul":6, "Aug":7, "Sep":8, "Oct":9, "Nov":10, "Dec":11}
    return calendar.get(month)

def visit_type(visit):
    
    if visit == "Returning_Visitor":
        return 1
    else:
        return 0

def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors= 1)
    model.fit(evidence, labels)

    return model
    

def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    total_pos = 0
    predicted_pos = 0 
    total_neg = 0
    predicted_neg = 0

    for a, b in zip(labels, predictions):
        if a == 1:
            total_pos += 1
            if a == b:
                predicted_pos += 1
        else:
            total_neg += 1
            if a == b :
                predicted_neg += 1

        
    return (predicted_pos/total_pos, predicted_neg/total_neg)


if __name__ == "__main__":
    main()
