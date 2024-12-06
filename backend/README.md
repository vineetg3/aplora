# Build the image
docker build -t aplora-app .

# Run the container with environment variable
docker run -p 5001:5001 -e OPENAI_API_KEY=your-key aplora-app