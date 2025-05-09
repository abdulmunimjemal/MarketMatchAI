from langchain_community.embeddings import OpenAIEmbeddings

# Create an instance with different parameter styles to see which one works
try:
    emb1 = OpenAIEmbeddings(api_key="test_key")
    print("api_key parameter works")
except Exception as e:
    print(f"api_key failed: {e}")

try:
    emb2 = OpenAIEmbeddings(openai_api_key="test_key")
    print("openai_api_key parameter works")
except Exception as e:
    print(f"openai_api_key failed: {e}")

# Print the class docstring to see documentation
print("\nDocumentation:")
print(OpenAIEmbeddings.__init__.__doc__)