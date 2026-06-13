import matplotlib.pyplot as plt

# Sample data
data = [7, 8, 15, 18, 20, 21, 25, 30, 45]
data2 = [7, 8, 15, 18, 20, 21, 25, 30, 45]

# Create the plot
plt.boxplot([data, data2] )

# Add labels
plt.title('Basic Box Plot')
plt.ylabel('Values')

# Show the plot
plt.show()
