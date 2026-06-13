import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
iris = sns.load_dataset('iris')

# style used as a theme of graph 
# for example if we want black 
# graph with grid then write "darkgrid"
sns.set_style("whitegrid")

# sepal_length, petal_length are iris
# feature data height used to define
# Height of graph whereas hue store the
# class of iris dataset.
sns.FacetGrid(iris, hue ="species", 
              height = 6).map(plt.scatter, 
                              'sepal_length', 
                              'petal_length').add_legend()
plt.show()