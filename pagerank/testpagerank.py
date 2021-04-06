import pagerank as pr
my_dicy = {
        "1.html": {"2.html", "3.html"},
        "2.html": {"3.html"}, 
        "3.html": {"2.html"}}

pr.iterate_pagerank(my_dicy, 0.85)
