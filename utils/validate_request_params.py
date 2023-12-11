"""
Validates the request parameters for the algorithm endpoints
Request structure is expected as (e.g.):
{
    "xVals": [1, 2, 3, 4, 5],
    "yVals": [1, 2, 3, 4, 5],
    "zVals": [1, 2, 3, 4, 5],
    "timeVals": [1, 2, 3, 4, 5],
    "testName": "test"
}
"""
def validate_request_params(request):
    try:
        if request.method == "POST":
            if request.json:
                if "xVals" in request.json and "yVals" in request.json and "zVals" in request.json and "timeVals" in request.json and "testName" in request.json:
                    return {
                        "success": True,
                        "message": "Valid request parameters"
                    }
        return {
            "success": False,
            "message": "Invalid request parameters"
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }