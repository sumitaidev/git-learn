import pandas as pd
import matplotlib.pyplot as plt
iris = pd.read_csv("Iris.csv")

plt.plot(iris['Id'], iris["PetalWidthCm"], "r",color="red")
plt.show()
print("this project is done by sumit")
