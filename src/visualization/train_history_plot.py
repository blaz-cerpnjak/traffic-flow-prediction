import matplotlib.pyplot as plt

def create_plot(history, title):
    plt.figure(figsize=(10, 6))

    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')

    plt.title(title)
    plt.xlabel('Epoch')
    plt.ylabel('Metrics')
    plt.legend()
    return plt