from langchain_community.embeddings import OpenAIEmbeddings

# Create an instance with different parameter styles to see which one works
try:
    emb1 = OpenAIEmbeddings(api_key="test_key")
    print("api_key parameter works")
except Exception as e:
    print(f"api_key failed: {e}")

try:
    emb2 = OpenAIEmbeddings(api_key="test_key", model="text-embedding-ada-002")
    print("api_key with model parameter works")
except Exception as e:
    print(f"api_key with model failed: {e}")

# Print the class docstring to see documentation
print("\nDocumentation:")
print(OpenAIEmbeddings.__init__.__doc__)