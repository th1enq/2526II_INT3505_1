package handlers

import (
	"net/http"
	"strconv"
	"sync"

	"demo-restful-api/models"

	"github.com/gin-gonic/gin"
)

// In-memory storage for demo
var (
	users   = map[int]*models.User{}
	nextID  = 1
	usersMu sync.RWMutex
)

func init() {
	// Seed some sample users
	users[1] = &models.User{ID: 1, Name: "Nguyen Van A", Email: "nguyenvana@example.com", Age: 25, IsActive: true}
	users[2] = &models.User{ID: 2, Name: "Tran Thi B", Email: "tranthib@example.com", Age: 30, IsActive: true}
	users[3] = &models.User{ID: 3, Name: "Le Van C", Email: "levanc@example.com", Age: 22, IsActive: false}
	nextID = 4
}

// GetAllUsers godoc
// @Summary      Get all users
// @Description  Returns a list of all users in the system. Demonstrates HTTP 200 OK.
// @Tags         Users
// @Produce      json
// @Success      200  {object}  models.SuccessResponse{data=[]models.User}  "List of users"
// @Router       /users [get]
func GetAllUsers(c *gin.Context) {
	usersMu.RLock()
	defer usersMu.RUnlock()

	list := make([]*models.User, 0, len(users))
	for _, u := range users {
		list = append(list, u)
	}

	c.JSON(http.StatusOK, models.SuccessResponse{
		Code:    http.StatusOK,
		Message: "OK - Successfully retrieved user list",
		Data:    list,
	})
}

// GetUserByID godoc
// @Summary      Get user by ID
// @Description  Returns detailed information of a user. Demonstrates HTTP 200, 400, 404.
// @Tags         Users
// @Produce      json
// @Param        id   path      int  true  "User ID"
// @Success      200  {object}  models.SuccessResponse{data=models.User}  "User information"
// @Failure      400  {object}  models.ErrorResponse  "Invalid ID"
// @Failure      404  {object}  models.ErrorResponse  "User not found"
// @Router       /users/{id} [get]
func GetUserByID(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		// 400 Bad Request
		c.JSON(http.StatusBadRequest, models.ErrorResponse{
			Code:    http.StatusBadRequest,
			Message: "Bad Request",
			Detail:  "ID must be a valid integer",
		})
		return
	}

	usersMu.RLock()
	user, exists := users[id]
	usersMu.RUnlock()

	if !exists {
		// 404 Not Found
		c.JSON(http.StatusNotFound, models.ErrorResponse{
			Code:    http.StatusNotFound,
			Message: "Not Found",
			Detail:  "User not found with ID = " + strconv.Itoa(id),
		})
		return
	}

	// 200 OK
	c.JSON(http.StatusOK, models.SuccessResponse{
		Code:    http.StatusOK,
		Message: "OK - Successfully retrieved user information",
		Data:    user,
	})
}

// CreateUser godoc
// @Summary      Create a new user
// @Description  Creates a new user in the system. Demonstrates HTTP 201 Created, 400 Bad Request, 409 Conflict.
// @Tags         Users
// @Accept       json
// @Produce      json
// @Param        user  body      models.CreateUserRequest  true  "User information to create"
// @Success      201   {object}  models.SuccessResponse{data=models.User}  "User created successfully"
// @Failure      400   {object}  models.ErrorResponse  "Invalid request data"
// @Failure      409   {object}  models.ErrorResponse  "Email already exists"
// @Failure      500   {object}  models.ErrorResponse  "Server error"
// @Router       /users [post]
func CreateUser(c *gin.Context) {
	var req models.CreateUserRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		// 400 Bad Request - validation failed
		c.JSON(http.StatusBadRequest, models.ErrorResponse{
			Code:    http.StatusBadRequest,
			Message: "Bad Request",
			Detail:  "Invalid data: " + err.Error(),
		})
		return
	}

	usersMu.Lock()
	defer usersMu.Unlock()

	// Check duplicate email – 409 Conflict
	for _, u := range users {
		if u.Email == req.Email {
			c.JSON(http.StatusConflict, models.ErrorResponse{
				Code:    http.StatusConflict,
				Message: "Conflict",
				Detail:  "Email '" + req.Email + "' is already in use by another user",
			})
			return
		}
	}

	newUser := &models.User{
		ID:       nextID,
		Name:     req.Name,
		Email:    req.Email,
		Age:      req.Age,
		IsActive: true,
	}
	users[nextID] = newUser
	nextID++

	// 201 Created
	c.JSON(http.StatusCreated, models.SuccessResponse{
		Code:    http.StatusCreated,
		Message: "Created - User created successfully",
		Data:    newUser,
	})
}

// UpdateUser godoc
// @Summary      Full update of a user (PUT)
// @Description  Replaces all user information. Demonstrates HTTP 200, 400, 404.
// @Tags         Users
// @Accept       json
// @Produce      json
// @Param        id    path      int                       true  "User ID"
// @Param        user  body      models.UpdateUserRequest  true  "Complete new user information"
// @Success      200   {object}  models.SuccessResponse{data=models.User}  "Update successful"
// @Failure      400   {object}  models.ErrorResponse  "Invalid data"
// @Failure      404   {object}  models.ErrorResponse  "User not found"
// @Router       /users/{id} [put]
func UpdateUser(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, models.ErrorResponse{
			Code:    http.StatusBadRequest,
			Message: "Bad Request",
			Detail:  "ID must be a valid integer",
		})
		return
	}

	var req models.UpdateUserRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, models.ErrorResponse{
			Code:    http.StatusBadRequest,
			Message: "Bad Request",
			Detail:  "Invalid data: " + err.Error(),
		})
		return
	}

	usersMu.Lock()
	defer usersMu.Unlock()

	user, exists := users[id]
	if !exists {
		c.JSON(http.StatusNotFound, models.ErrorResponse{
			Code:    http.StatusNotFound,
			Message: "Not Found",
			Detail:  "User not found with ID = " + strconv.Itoa(id),
		})
		return
	}

	// Full replacement
	user.Name = req.Name
	user.Email = req.Email
	user.Age = req.Age
	user.IsActive = req.IsActive

	c.JSON(http.StatusOK, models.SuccessResponse{
		Code:    http.StatusOK,
		Message: "OK - User fully updated successfully (PUT)",
		Data:    user,
	})
}

// PatchUser godoc
// @Summary      Partial update of a user (PATCH)
// @Description  Updates only the provided fields. Demonstrates HTTP 200, 400, 404.
// @Tags         Users
// @Accept       json
// @Produce      json
// @Param        id    path      int                      true  "User ID"
// @Param        user  body      models.PatchUserRequest  true  "Fields to update"
// @Success      200   {object}  models.SuccessResponse{data=models.User}  "Update successful"
// @Failure      400   {object}  models.ErrorResponse  "Invalid data"
// @Failure      404   {object}  models.ErrorResponse  "User not found"
// @Router       /users/{id} [patch]
func PatchUser(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, models.ErrorResponse{
			Code:    http.StatusBadRequest,
			Message: "Bad Request",
			Detail:  "ID must be a valid integer",
		})
		return
	}

	var req models.PatchUserRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, models.ErrorResponse{
			Code:    http.StatusBadRequest,
			Message: "Bad Request",
			Detail:  "Invalid data: " + err.Error(),
		})
		return
	}

	usersMu.Lock()
	defer usersMu.Unlock()

	user, exists := users[id]
	if !exists {
		c.JSON(http.StatusNotFound, models.ErrorResponse{
			Code:    http.StatusNotFound,
			Message: "Not Found",
			Detail:  "User not found with ID = " + strconv.Itoa(id),
		})
		return
	}

	// Partial update - only update fields that are provided
	if req.Name != nil {
		user.Name = *req.Name
	}
	if req.Email != nil {
		user.Email = *req.Email
	}
	if req.Age != nil {
		user.Age = *req.Age
	}
	if req.IsActive != nil {
		user.IsActive = *req.IsActive
	}

	c.JSON(http.StatusOK, models.SuccessResponse{
		Code:    http.StatusOK,
		Message: "OK - User partially updated successfully (PATCH)",
		Data:    user,
	})
}

// DeleteUser godoc
// @Summary      Delete a user
// @Description  Removes a user from the system. Demonstrates HTTP 204 No Content, 404 Not Found.
// @Tags         Users
// @Produce      json
// @Param        id   path  int  true  "User ID"
// @Success      204  "Deleted successfully, no content returned"
// @Failure      400  {object}  models.ErrorResponse  "Invalid ID"
// @Failure      404  {object}  models.ErrorResponse  "User not found"
// @Router       /users/{id} [delete]
func DeleteUser(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, models.ErrorResponse{
			Code:    http.StatusBadRequest,
			Message: "Bad Request",
			Detail:  "ID must be a valid integer",
		})
		return
	}

	usersMu.Lock()
	defer usersMu.Unlock()

	if _, exists := users[id]; !exists {
		c.JSON(http.StatusNotFound, models.ErrorResponse{
			Code:    http.StatusNotFound,
			Message: "Not Found",
			Detail:  "User not found with ID = " + strconv.Itoa(id),
		})
		return
	}

	delete(users, id)

	// 204 No Content
	c.Status(http.StatusNoContent)
}
