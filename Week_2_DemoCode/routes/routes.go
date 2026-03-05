package routes

import (
	"demo-restful-api/handlers"

	"github.com/gin-gonic/gin"
)

// SetupRoutes registers all API routes
func SetupRoutes(r *gin.Engine) {
	api := r.Group("/api/v1")
	{
		users := api.Group("/users")
		{
			users.GET("", handlers.GetAllUsers)       // GET    /api/v1/users
			users.POST("", handlers.CreateUser)       // POST   /api/v1/users
			users.GET("/:id", handlers.GetUserByID)   // GET    /api/v1/users/:id
			users.PUT("/:id", handlers.UpdateUser)    // PUT    /api/v1/users/:id
			users.PATCH("/:id", handlers.PatchUser)   // PATCH  /api/v1/users/:id
			users.DELETE("/:id", handlers.DeleteUser) // DELETE /api/v1/users/:id
		}

		demo := api.Group("/demo/status")
		{
			demo.GET("/1xx", handlers.Demo1xx) // GET /api/v1/demo/status/1xx?code=102
			demo.GET("/2xx", handlers.Demo2xx) // GET /api/v1/demo/status/2xx?code=200
			demo.GET("/3xx", handlers.Demo3xx) // GET /api/v1/demo/status/3xx?code=301
			demo.GET("/4xx", handlers.Demo4xx) // GET /api/v1/demo/status/4xx?code=404
			demo.GET("/5xx", handlers.Demo5xx) // GET /api/v1/demo/status/5xx?code=500
		}
	}
}
