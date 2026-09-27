from fastapi import HTTPException, status


class NumericalSolverError(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY):
        super().__init__(status_code=status_code, detail=detail)


class ConvergenceError(NumericalSolverError):
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class SingularMatrixError(NumericalSolverError):
    def __init__(self, detail: str = "Matrix is singular; system has no unique solution."):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
