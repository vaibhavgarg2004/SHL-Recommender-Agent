from agent import agent_reply

# =========================================================
# CHAT LOOP
# =========================================================

def run_chat():

    print("\n" + "=" * 80)
    print("SHL RECOMMENDATION AGENT")
    print("Type 'exit' to quit.")
    print("=" * 80 + "\n")

    messages = []

    while True:

        # =================================================
        # USER INPUT
        # =================================================

        user_input = input("\nYou: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print("\nEnding conversation.")
            break

        # =================================================
        # STORE MESSAGE
        # =================================================

        messages.append({
            "role": "user",
            "content": user_input
        })

        # =================================================
        # AGENT RESPONSE
        # =================================================

        response = agent_reply(messages)

        print("\nAgent:\n")

        print(response["reply"])

        # =================================================
        # STORE AGENT MESSAGE
        # =================================================

        messages.append({
            "role": "assistant",
            "content": response["reply"]
        })

        # =================================================
        # END CONVERSATION
        # =================================================

        if response["end_of_conversation"]:

            print("\nConversation completed.")
            break

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    run_chat()