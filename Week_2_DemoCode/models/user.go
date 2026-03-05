package models

// User represents a user in the system
// @Description User account information
type User struct {
	ID       int    `json:"id" example:"1"`
	Name     string `json:"name" example:"Nguyen Van A"`
	Email    string `json:"email" example:"nguyenvana@example.com"`
	Age      int    `json:"age" example:"25"`
	IsActive bool   `json:"is_active" example:"true"`
}

// CreateUserRequest represents the body when creating a user
// @Description Request body for creating a new user
type CreateUserRequest struct {
	Name  string `json:"name" binding:"required" example:"Nguyen Van A"`
	Email string `json:"email" binding:"required,email" example:"nguyenvana@example.com"`
	Age   int    `json:"age" binding:"required,min=1,max=150" example:"25"`
}

// UpdateUserRequest represents the body when fully updating a user
// @Description Request body for full update of a user (PUT)
type UpdateUserRequest struct {
	Name     string `json:"name" binding:"required" example:"Nguyen Van B"`
	Email    string `json:"email" binding:"required,email" example:"nguyenvanb@example.com"`
	Age      int    `json:"age" binding:"required,min=1,max=150" example:"30"`
	IsActive bool   `json:"is_active" example:"true"`
}

// PatchUserRequest represents the body for partial update
// @Description Request body for partial update of a user (PATCH)
type PatchUserRequest struct {
	Name     *string `json:"name,omitempty" example:"Nguyen Van C"`
	Email    *string `json:"email,omitempty" example:"nguyenvanc@example.com"`
	Age      *int    `json:"age,omitempty" example:"28"`
	IsActive *bool   `json:"is_active,omitempty" example:"false"`
}

// ErrorResponse represents error structure
// @Description Standard error response
type ErrorResponse struct {
	Code    int    `json:"code" example:"400"`
	Message string `json:"message" example:"Bad Request"`
	Detail  string `json:"detail,omitempty" example:"Field 'name' is required"`
}

// SuccessResponse represents success structure
// @Description Standard success response
type SuccessResponse struct {
	Code    int         `json:"code" example:"200"`
	Message string      `json:"message" example:"OK"`
	Data    interface{} `json:"data,omitempty"`
}
