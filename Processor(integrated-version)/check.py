import tensorflow as tf

def check_gpu():
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        print("GPUs are available:")
        for gpu in gpus:
            print(f"  - {gpu}")
    else:
        print("No GPUs found.")

if __name__ == "__main__":
    check_gpu()
