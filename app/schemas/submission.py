from pydantic import BaseModel


class SubmissionValidationError(BaseModel):
    field: str
    message: str


class SubmitProjectRequest(BaseModel):
    project_id: str


class SubmitProjectResponse(BaseModel):
    success: bool
    errors: list[SubmissionValidationError] = []
    shipped: bool = False
