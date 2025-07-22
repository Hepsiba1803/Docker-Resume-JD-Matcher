from sentence_transformers import SentenceTransformer
model = SentenceTransformer("intfloat/e5-small-v2")
model.save("local_models/intfloat-e5-small-v2")
