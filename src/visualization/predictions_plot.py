import matplotlib.pyplot as plt


def create_plot(df, predictions, title, subtitle):
    plt.figure(figsize=(20, 10))
    plt.plot(df.index[-len(predictions):], df['minutes'][-len(predictions):], label='Actual value')
    plt.plot(df.index[-len(predictions):], predictions, label='Prediction')

    plt.xlabel('Time')
    plt.ylabel('Available Bike Stands')
    plt.title(subtitle)
    plt.suptitle(title)

    plt.grid(False)
    plt.legend()
    plt.tight_layout()

    return plt