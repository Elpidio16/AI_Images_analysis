from flask import Flask, render_template, request
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import io
import base64

app = Flask(__name__)

# Configuration Azure
# Récupérer les clés stockées comme variables d'environnement dans Vercel
subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")
endpoint = os.getenv("AZURE_ENDPOINT")
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        return "Aucune image soumise.", 400

    image = request.files['image']
    image_data = image.read()

    # Encode l'image en base64 pour l'afficher dans la page HTML
    encoded_image_data = base64.b64encode(image_data).decode('utf-8')

    # Créez un flux à partir des données binaires
    image_stream = io.BytesIO(image_data)

    # Analyse de l’image
    analysis_result = computervision_client.analyze_image_in_stream(
        image_stream, visual_features=["Description", "Tags", "Objects"]
    )

    description = analysis_result.description.captions[0].text if analysis_result.description.captions else "Pas de description disponible."
    tags = [tag.name for tag in analysis_result.tags]
    objects = [(obj.object_property, obj.confidence) for obj in analysis_result.objects]
    
    return render_template('result.html', image_data=encoded_image_data, description=description, tags=tags, objects=objects)

if __name__ == '__main__':
    app.run(debug=True)
