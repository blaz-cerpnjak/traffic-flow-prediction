import matplotlib.pyplot as plt


def create_plot(df, predictions, title, subtitle, x_label, y_label, target='minutes'):
    plt.figure(figsize=(20, 10))
    plt.plot(df.index[-len(predictions):], df[target][-len(predictions):], label='Actual value')
    plt.plot(df.index[-len(predictions):], predictions, label='Prediction')

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(subtitle)
    plt.suptitle(title)

    plt.grid(False)
    plt.legend()
    plt.tight_layout()

    return plt