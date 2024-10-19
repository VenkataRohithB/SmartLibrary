import uvicorn

from fastapi import FastAPI
from common_auth import router as auth_router
from sl_users import router as user_router
from sl_otp import router as otp_router
from sl_books import router as books_router
from sl_library import router as library_router
from sl_transactions import router as transaction_router
app = FastAPI(
    title="Smart Library",
    description=(
        "Smart Library is a comprehensive library management system designed for "
        "effortless access and management of books. \n\n"
        "Key Features:\n"
        "- Streamlined user interactions for book rentals and returns.\n"
        "- Integrated user check-in/check-out functionality.\n"
        "- Real-time tracking of book availability and user transactions.\n"
        "- Support for penalty management to ensure accountability.\n\n"
        "Experience a hassle-free way to manage your reading journey with Smart Library."
    )
)

app.include_router(library_router, tags=["library"])
app.include_router(books_router, tags=["books"])
app.include_router(transaction_router, tags=["transactions"])
app.include_router(user_router, tags=["users"])
app.include_router(otp_router, tags=["otp"])
app.include_router(auth_router, tags=["auth"])

uvicorn.run(app=app, host="0.0.0.0", port=8000)
