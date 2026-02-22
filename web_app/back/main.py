from typing import Union
from io import BytesIO
import asyncio
import json
from scapy.all import rdpcap
from models.preprocessing_netmamba import split_pcap_file,pcap_to_array,split_pcap_file_single
from models.preprocessing_yatc import MFR_generator_yatc
from models.classification_yatc import yatc_inference
from models.classification_netmamba import netMamba_classification
from models.classification_lstm import lstm_inference
from models.classification_etbert import etbert_inference
from models.processing_etbert_lstm import get_feature_packet
from models.config import aggregate_model_predictions,packet_stat

from fastapi import FastAPI,File ,UploadFile,Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


app= FastAPI()
templates = Jinja2Templates(directory="front")

# Configuration
CONFIDENCE_THRESHOLD = 0.80
CONFIDENCE_THRESHOLD_lstm = 0.20

DATASETS = ["USTC_TFC2016", "CICIOT2022", "ISCX_VPN2016", "ISCX_TOR2016"]
# Storage for background processing
# Storage for background processing
app.state.processing = False
app.state.results = None
app.state.last_uploaded_bytes = None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/upload_pcap_file", response_class=HTMLResponse)
async def upload_file(request: Request, fileUpload: UploadFile):
    print("Received:", fileUpload.filename)

    file_type = fileUpload.filename.split(".")[-1]
    if file_type != "pcap":
        return templates.TemplateResponse(
            name="error_file.html", context={"request": request}
        )

    # Read file bytes (fast)
    file_bytes = await fileUpload.read()
    request.app.state.last_uploaded_bytes = file_bytes

    # Reset results and start background PCAP processing
    request.app.state.results = None
    request.app.state.processing = True
    asyncio.create_task(process_pcap(request.app))

    # Immediately return a polling div
    return HTMLResponse("""
        <div hx-get="/upload_status"
             hx-trigger="every 1000ms"
             hx-target="#results"
             hx-swap="innerHTML">
            <div class="text-blue-300 text-center">Processing PCAP…</div>
        </div>
    """)

async def process_pcap(app: FastAPI):
    print("Background task started…")
    
    try:
        file_bytes = app.state.last_uploaded_bytes
        packets = rdpcap(BytesIO(file_bytes))

        # Check if PCAP has valid flows with at least 5 packets
        split_result = await split_pcap_file_single(packets)
        
        if "error" in split_result:
            # Store error and stop processing
            app.state.results = {"error": split_result["error"]}
            app.state.processing = False
            return

        # Continue with normal processing
        stats = packet_stat(packets)
        MFR_generator_yatc()  # generate dataset for yatc
        pcap_to_array()  # generate dataset for netmamba
        processed_packets = await get_feature_packet()

        yatc_predictions = yatc_inference()
        lstm_predictions = lstm_inference(processed_packets)
        etbert_predictions = etbert_inference(processed_packets)
        netmamba_predictions = netMamba_classification()
        
        print("netMamba prediction")
        print(netmamba_predictions)
        print("yatc prediction")
        print(yatc_predictions)
            
        results = aggregate_model_predictions({
            "lstm": lstm_predictions,
            "YATC": yatc_predictions,
            "ETBERT": etbert_predictions,
            "NetMamba": netmamba_predictions
        })

        # Save results for UI polling
        app.state.results = {
            "lstm": results["lstm"],
            "YATC": results["YATC"],
            "ETBERT": results["ETBERT"],
            "NetMamba": results["NetMamba"],
            "final_decision": results["final_decision"],
            "stats": stats
        }

    except Exception as e:
        print(f"Error in process_pcap: {e}")
        import traceback
        traceback.print_exc()
        app.state.results = {"error": f"Processing failed: {str(e)}"}

    finally:
        app.state.processing = False
        print("Background task finished.")


@app.get("/upload_status", response_class=HTMLResponse)
async def upload_status(request: Request):
    # Still working?
    if request.app.state.processing:
        return HTMLResponse("""
            <div class="text-blue-300 text-center">
                Processing PCAP file… still working…
            </div>
        """)

    # Get results
    data = request.app.state.results
    
    # Race condition - nothing ready yet
    if data is None:
        return HTMLResponse("""
            <div class="text-yellow-300 text-center">
                Finalizing results…
            </div>
        """)

    # Error during processing?
    if "error" in data:
        return HTMLResponse("""
        <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div class="bg-gray-900 text-white p-6 rounded-lg shadow-xl max-w-md">
                <h2 class="text-xl font-bold text-red-400 mb-4">
                    ⚠ PCAP Processing Error
                </h2>
                <p class="mb-4">
                    """ + data["error"] + """
                    <br><br>Please upload a valid PCAP file with network flows containing at least 5 packets each.
                </p>
                <button onclick="location.href='/'"
                        class="bg-red-500 hover:bg-red-600 px-4 py-2 rounded">
                    OK
                </button>
            </div>
        </div>
        """)

    # Prepare context for results.html
    context = {
        "result_present": True,
        "request": request,
        "models": {
            "lstm": data["lstm"],
            "YATC": data["YATC"],
            "ETBERT": data["ETBERT"],
            "NetMamba": data["NetMamba"]
        },
        "final_decision": data["final_decision"],
        "metadata": {
            "tcp": data["stats"]["TCP"],
            "udp": data["stats"]["UDP"]
        }
    }

    return templates.TemplateResponse("results.html", context)



def pcaps_to_img():
    booleen =pcap_to_array()
    return booleen


@app.get("/reset",response_class=HTMLResponse)
def reset(request:Request):
    context={
        "request":request,
        "result_present":False,
    }
    return templates.TemplateResponse(name="results.html", context=context)



#legacy code
@app.post("/upload_pcap_file_total", response_class=HTMLResponse)
async def upload_file_total(request: Request, fileUpload: UploadFile):
    """
    Process uploaded PCAP file and return classification results.
    """
    print("Controller received file:", fileUpload.filename)
    file_type=fileUpload.filename.split('.')[-1]
    if file_type !="pcap":
        return  templates.TemplateResponse(request=request,name="error_file.html")
    #try:
    # Read and process PCAP file
    file_bytes = await fileUpload.read()
    packets = rdpcap(BytesIO(file_bytes))
    
    # Processing pipeline
    number_flows = await split_pcap_file_single(packets)
    stats=packet_stat(packets)
   

    MFR_generator_yatc() #generate dataset for 
    processed_packets = await get_feature_packet()
    #print(processed_packets)
    
    # Run inference on all models
    yatc_output = yatc_inference()
    lstm_output = lstm_inference(processed_packets)
    etbert_output = etbert_inference(processed_packets)
    #print(lstm_output)
    #print(etbert_output)
    print("Raw outputs received from models")

    # Process logits to probabilities for each dataset
    yatc_predictions = process_yatc_logits(yatc_output)
    lstm_predictions = process_lstm_logits(lstm_output)
    etbert_predictions = process_etbert_logits(etbert_output)
    print(lstm_predictions)
    print(etbert_predictions)
    print(yatc_predictions)
    
    # Aggregate all predictions
    all_predictions = {
        "lstm": lstm_predictions,
        "YATC": yatc_predictions,
        "ETBERT": etbert_predictions
    }
    
    # Get final aggregated results
    results = aggregate_model_predictions(all_predictions)
    print(results)
    
    
    print("Final classification results:", json.dumps(results, indent=2))
    
    # Prepare context for template
    context = {
        "result_present":True,
        "request": request,
        "models": {
            "lstm": results["lstm"],
            "YATC": results["YATC"],
            "ETBERT": results["ETBERT"]
        },
        "final_decision": results["final_decision"],
        "metadata": {
            "tcp": stats['TCP'],
            "udp": stats['UDP']
        }
    }
    
    return templates.TemplateResponse(name="results.html", context=context)
    """    
    except Exception as e:
        print(f"Error processing PCAP: {str(e)}")
        error_context = {
            "request": request,
            "error": str(e)
        }
        return templates.TemplateResponse(name="error.html", context=error_context)

    """
