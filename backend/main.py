from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv
import mimetypes

load_dotenv()

# Explicitly register mimetypes to fix minimal Ubuntu servers lacking the 'media-types' registry,
# which otherwise causes HTML/PDF exports to be served as plain text 'txt' files
mimetypes.add_type("text/html", ".html")
mimetypes.add_type("application/pdf", ".pdf")
mimetypes.add_type("image/jpeg", ".jpg")
mimetypes.add_type("text/markdown", ".md")

from services.search_service import search_book_info
from services.llm_service import extract_quotes, generate_core_thought, generate_mindmap_markdown
from services.image_service import generate_image
from services.poster_service import create_poster_image
from services.document_service import generate_mindmap_document

from database import engine, Base
import models
from routers.h5_api import router as h5_router

app = FastAPI(title="Book Quote Generator API")

# Initialize SQLite database schema
Base.metadata.create_all(bind=engine)

# Include H5 App specialized router
app.include_router(h5_router)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import FileResponse
from fastapi import HTTPException

# Serve static files explicitly to bypass missing Ubuntu mimetypes registries
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)

@app.get("/static/{filename}")
async def get_static_file(filename: str):
    file_path = os.path.join(static_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    mime_type = None
    if filename.endswith(".html"):
        mime_type = "text/html"
    elif filename.endswith(".pdf"):
        mime_type = "application/pdf"
    elif filename.endswith(".jpg") or filename.endswith(".jpeg"):
        mime_type = "image/jpeg"
    elif filename.endswith(".md"):
        mime_type = "text/markdown"
        
    return FileResponse(file_path, media_type=mime_type)

class GetQuotesRequest(BaseModel):
    book_title: str

class GetQuotesResponse(BaseModel):
    quotes: list[str]
    message: str

class GeneratePosterRequest(BaseModel):
    book_title: str
    selected_quotes: list[str]
    generate_image: bool = True

class GeneratePosterResponse(BaseModel):
    poster_url: str
    image_url: str | None = None
    core_thought: str | None = None
    message: str

class GenerateMindmapRequest(BaseModel):
    book_title: str

class GenerateMindmapResponse(BaseModel):
    pdf_url: str
    message: str

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Book Quote Generator API is running"}

@app.post("/api/get_quotes", response_model=GetQuotesResponse)
async def get_quotes(request: GetQuotesRequest):
    try:
        print(f"1. Searching info for: {request.book_title}")
        context = search_book_info(request.book_title)
        
        print(f"2. Extracting 10 quotes...")
        quotes = extract_quotes(request.book_title, context)
        
        return GetQuotesResponse(quotes=quotes, message="Success")
    except Exception as e:
        print(f"Error in fetching quotes: {e}")
        return GetQuotesResponse(quotes=[], message=f"Error: {e}")

@app.post("/api/generate_poster", response_model=GeneratePosterResponse)
async def generate_poster(request: GeneratePosterRequest):
    try:
        core_thought = None
        image_url = None
        
        # Searching info again (in production this would be cached or passed along)
        context = search_book_info(request.book_title)
        
        if request.generate_image:
            print(f"3a. Generating core thought from overall book context...")
            core_thought = generate_core_thought(request.book_title, context)
            
            print(f"3b. Generating background image based on core thought...")
            image_url = generate_image(core_thought)
        
        print(f"4. Creating poster...")
        poster_local_path = await create_poster_image(request.book_title, request.selected_quotes, image_url)
        
        return GeneratePosterResponse(
            poster_url=poster_local_path,
            image_url=image_url if request.generate_image else "",
            core_thought=core_thought if request.generate_image else "使用纯色纯文字排版。",
            message="Success"
        )
    except Exception as e:
        print(f"Error in creating poster: {e}")
        return GeneratePosterResponse(
            poster_url="",
            message=f"Error generating poster: {str(e)}"
        )

@app.post("/api/generate_mindmap", response_model=GenerateMindmapResponse)
async def generate_mindmap(request: GenerateMindmapRequest):
    try:
        print(f"1. Searching info for Mindmap: {request.book_title}")
        context = search_book_info(request.book_title)
        
        print(f"2. Generating Markdown structure...")
        md_content = generate_mindmap_markdown(request.book_title, context)
        
        print(f"3. Rendering Document using Markmap...")
        pdf_url = generate_mindmap_document(request.book_title, md_content)
        
        return GenerateMindmapResponse(pdf_url=pdf_url, message="Success")
    except Exception as e:
        print(f"Error in creating mindmap: {e}")
        return GenerateMindmapResponse(pdf_url="", message=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
