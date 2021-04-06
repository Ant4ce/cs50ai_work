import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    prob_persons = [] 
    final_probab = 1

    for person in people:
        our_prob_list = get_list_probab(people, one_gene, two_genes, person)
        if person in one_gene:
            if people[person]["mother"] is None and people[person]["father"] is None:
                prob_persons.append(prob_with_trait(have_trait, person, 1))
            else:
                probability_for_individual = our_prob_list[0][0] * our_prob_list[1][1] + our_prob_list[0][1] * our_prob_list[1][0]   
                #appends the prob based on calculation of inheriting traits from known parents
                prob_persons.append(prob_with_parents_and_trait(have_trait, probability_for_individual, person, 1))
        elif person in two_genes:
            if people[person]["mother"] is None and people[person]["father"] is None:
                prob_persons.append(prob_with_trait(have_trait, person, 2))
            else:
                probability_for_individual = our_prob_list[0][0] * our_prob_list[1][0] 
                prob_persons.append(prob_with_parents_and_trait(have_trait, probability_for_individual, person, 2))
        else:
            if people[person]["mother"] is None and people[person]["father"] is None:
                prob_persons.append(prob_with_trait(have_trait, person, 0))
            else:
                probability_for_individual = our_prob_list[0][1] * our_prob_list[1][1]
                prob_persons.append(prob_with_parents_and_trait(have_trait, probability_for_individual, person, 0))

    for every in prob_persons:
        final_probab = final_probab * every

    return final_probab

def prob_with_parents_and_trait(have_trait, prob_indiv, person, num):
    value_prob = prob_indiv
    if person in have_trait:
        value_prob = value_prob * PROBS["trait"][num][True]
    else:
        value_prob = value_prob * PROBS["trait"][num][False]
        
    return value_prob

def prob_with_trait(have_trait, person, num):
    if person in have_trait:
        return PROBS["gene"][num] * PROBS["trait"][num][True]
    else:
        return PROBS["gene"][num] * PROBS["trait"][num][False]

def get_list_probab(people,one_gene, two_genes, person):
    mom_dad = []
    words_md = ["mother","father"]
    for each in words_md:
        for parent in people:
            if parent == people[person][each]:
                if parent in one_gene:
                    #the prob that the parent carries over her gene or not are 50/50, the first one represents that it does carry over
                    mom_dad.append([PROBS["mutation"] * 0.5 + (1 - PROBS["mutation"]) * 0.5,PROBS["mutation"] * 0.5 + (1 - PROBS["mutation"]) * 0.5])
                elif parent in two_genes:
                    mom_dad.append([1 - PROBS["mutation"],PROBS["mutation"]])
                else:
                    mom_dad.append([PROBS["mutation"],1 - PROBS["mutation"]])

    return mom_dad


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        if person in one_gene:
            probabilities[person]["gene"][1] += p 
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
        else:
            probabilities[person]["gene"][0] += p

        if person in have_trait:
            probabilities[person]["trait"][True] += p
        else:
            probabilities[person]["trait"][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    num_list = [0,1,2]
    type_list = ["gene", "trait"]
    bool_list = [True, False]
    sum_list_trait = []
    sum_list_gene = []
    for person in probabilities:
        for typing in type_list:
            if typing == "gene":
                for num in num_list:
                    sum_list_gene.append(probabilities[person][typing][num])
            if typing == "trait":
                for boel in bool_list:
                    sum_list_trait.append(probabilities[person][typing][boel])

        sum_gene = sum(sum_list_gene)
        sum_trait = sum(sum_list_trait)

        for typing in type_list:
            if typing == "gene":
                for num in num_list:
                    probabilities[person][typing][num] = sum_list_gene[num]/sum_gene
            if typing == "trait":
                for boel in bool_list:
                    if boel == True:
                        probabilities[person][typing][boel] = sum_list_trait[0]/sum_trait
                    if boel == False:
                        probabilities[person][typing][boel] = sum_list_trait[1]/sum_trait

        sum_list_trait = []
        sum_list_gene = []
            
                    
    

if __name__ == "__main__":
    main()
