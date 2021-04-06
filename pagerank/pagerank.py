import os
import random
import re
import sys
import numpy as np

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    #gets the values of the connected pages to the current page
    connected_pages = corpus[page]
    #get list of the keys of the dict and thus all the pages in the corpus
    keys_list = corpus.keys()
    odds_equal = 1/len(keys_list)
    if len(connected_pages) == 0: 
        equals_dict = dict.fromkeys(keys_list, odds_equal)
        return equals_dict

    odds_initial_page = DAMPING * (1/len(connected_pages)) 
    odds_rand_page = (1 - DAMPING) * odds_equal 
    
    new_keys = []
    new_odds = []
    for each in keys_list:
        if each in connected_pages:
            new_keys.append(each)
            new_odds.append(odds_initial_page + odds_rand_page)
        else:
            new_keys.append(each)
            new_odds.append(odds_rand_page)
    
    dict_return = dict(zip(new_keys, new_odds))
    return dict_return
            


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    keys_list = corpus.keys()
    return_dict = dict.fromkeys(keys_list, 0)

    # get the first page by looking at all the keys
    first_page = random.choice(list(corpus.keys()))
    return_dict[first_page] += 1

    transtition_state = transition_model(corpus, first_page, damping_factor)

    i = 0
    list_of_picks = []
    # n-1 because we already added the initial page to the list
    while i < (n-1):
        next_sample_pick = np.random.choice(list(transtition_state.keys()), 1, p= list(transtition_state.values()))
        list_of_picks.append(next_sample_pick[0])
        return_dict[next_sample_pick[0]] += 1
        transtition_state = transition_model(corpus, next_sample_pick[0], damping_factor)
        i += 1
    return_dict = {key: return_dict[key] / n for key in return_dict.keys()}

    return return_dict
        


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    keys_list = corpus.keys()
    number_of_pages = len(keys_list)
    #creating a dict where we assume the pagerank for each page to be equal.
    return_dict = dict.fromkeys(keys_list, 1/number_of_pages)

    while True:

        difference_list = []
        pr_list = []

        for page in corpus:
            for target in corpus:
                if page == target:
                    continue

                if corpus[target] is None:
                    no_link_page = return_dict[target] / number_of_pages
                    pr_list.append(no_link_page)

                if page in corpus[target]:
                    num_links = len(corpus[target])
                    page_rank_current = return_dict[target]
                    pr_links_value = page_rank_current / num_links
                    pr_list.append(pr_links_value)

            odds_page = ((1-damping_factor)/number_of_pages) +(damping_factor * sum(pr_list))
            difference_list.append(abs(return_dict[page] - odds_page))
            return_dict[page] = odds_page
            pr_list = []

        difference = sum(difference_list)/number_of_pages
        difference_list = []

        #note: deppending on how low the number here is made the more the result will
        # approach 1 when summing all the values. It seems to be right it's a matter of
        # precision
        if difference < 0.00001:
            break


    return return_dict



if __name__ == "__main__":
    main()
