import time
import ollama
import torch


def chat_evaluation(model_name, BATCH_ITERS=8):
    SHARED_PROMPT = (
        "You are a friendly chatbot. Have a nice conversation with the user."
    )
    messages_A = [{"role": "system", "content": SHARED_PROMPT}]

    messages_B = [{"role": "system", "content": SHARED_PROMPT}]

    context_count = len(messages_A[0]["content"])
    data = []

    for i in range(BATCH_ITERS):
        ithstart = time.time()
        if i % 2 == 0:
            print(messages_A)
            response = ollama.chat(model=model_name, messages=messages_A)
            messages_B.append(
                {"role": "user", "content": response["message"]["content"]}
            )
            messages_A.append(
                {"role": "assistant", "content": response["message"]["content"]}
            )
        if i % 2 == 1:
            print(messages_B)
            response = ollama.chat(model=model_name, messages=messages_B)
            messages_A.append(
                {"role": "user", "content": response["message"]["content"]}
            )
            messages_B.append(
                {"role": "assistant", "content": response["message"]["content"]}
            )

        ithend = time.time()
        ithelapsed = ithend - ithstart
        chars_inferenced_this_round = len(response["message"]["content"])

        datum = (ithelapsed, context_count, chars_inferenced_this_round)
        with open(f"./chat_evaluation_data_{model_name}.txt", "a") as f:
            f.write(f"{datum}\n")
        data.append((ithelapsed, context_count, chars_inferenced_this_round))
        context_count += chars_inferenced_this_round

    return data


def make_headers(model_name):
    header = f"Model:\n{model_name}\n"
    header += "Devices:"
    if torch.cuda.is_available():
        num_devices = torch.cuda.device_count()

        for i in range(num_devices):
            header += "\n"
            header += torch.cuda.get_device_name(i)
    else:
        header += "\nCPU"

    header += "\nTime Elapsed (s), Context Count, Characters Inferenced"
    header += "\n-----------------------------------\n"

    return header


def main(model_name):
    with open(f"./chat_evaluation_data_{model_name}.txt", "w") as f:
        f.write(make_headers(model_name))

    ollama.pull(model_name)
    # ensure model is loaded
    ollama.generate(model=model_name, prompt="Say one word")
    print("starting evaluation")
    # evaluate model
    for _ in range(3):
        data = chat_evaluation(model_name)


if __name__ == "__main__":
    model_list = ["command-r", "llama3"]
    for model_name in model_list:
        main(model_name)
    print("run complete")
