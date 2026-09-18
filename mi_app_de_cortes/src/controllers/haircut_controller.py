from fastapi import APIRouter, File, UploadFile, HTTPException
from mi_app_de_cortes.src.services import haircut_service
from mi_app_de_cortes.src.models.recommend import RecommendResponse

router = APIRouter()


@router.post("/analyze")
async def analyze_photo(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        haircut_service.validate_image(image_bytes, file.content_type)
        analysis = haircut_service.analyze_face(image_bytes, file.content_type)
        return {"success": True, "analysis": analysis}
    except ValueError as e:
        status_code = 413 if "10MB" in str(e) else 400
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")


@router.post("/recommend", response_model=RecommendResponse)
async def recommend_haircut(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        haircut_service.validate_image(image_bytes, file.content_type)
        analysis = haircut_service.analyze_face(image_bytes, file.content_type)
        recommendations = haircut_service.generate_recommendations(image_bytes, analysis)
        return RecommendResponse(success=True, recommendations=recommendations)
    except ValueError as e:
        status_code = 413 if "10MB" in str(e) else 400
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")
