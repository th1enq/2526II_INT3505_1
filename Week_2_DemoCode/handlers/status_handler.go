package handlers

import (
	"net/http"

	"demo-restful-api/models"

	"github.com/gin-gonic/gin"
)

// Demo1xx godoc
// @Summary      Demo 1xx status codes - Informational
// @Description  Demonstrates 1xx status codes. In HTTP/1.1, 102 Processing indicates the server is working but hasn't finished yet.
// @Description  **Note:** 1xx codes are not normally used directly in REST API response bodies; this demo simulates them via JSON.
// @Tags         HTTP Status Codes Demo
// @Produce      json
// @Param        code  query  int  false  "1xx status code to demo (100, 101, 102, 103)"  Enums(100, 101, 102, 103)
// @Success      100   {object}  models.SuccessResponse  "Continue"
// @Success      101   {object}  models.SuccessResponse  "Switching Protocols"
// @Success      102   {object}  models.SuccessResponse  "Processing"
// @Success      103   {object}  models.SuccessResponse  "Early Hints"
// @Router       /demo/status/1xx [get]
func Demo1xx(c *gin.Context) {
	codeStr := c.DefaultQuery("code", "102")
	code := 102
	switch codeStr {
	case "100":
		code = 100
	case "101":
		code = 101
	case "102":
		code = 102
	case "103":
		code = 103
	}

	messages := map[int]string{
		100: "Continue - Server has received the initial part of the request, client should continue sending",
		101: "Switching Protocols - Server is switching to the protocol requested by the client",
		102: "Processing - Server is processing the request (WebDAV), not yet complete",
		103: "Early Hints - Server sends preliminary headers before the main response",
	}

	c.JSON(code, models.SuccessResponse{
		Code:    code,
		Message: messages[code],
		Data:    map[string]string{"info": "1xx: Informational - Request received, processing in progress"},
	})
}

// Demo2xx godoc
// @Summary      Demo 2xx status codes - Success
// @Description  Demonstrates success codes: 200 OK, 201 Created, 202 Accepted, 204 No Content, 206 Partial Content.
// @Tags         HTTP Status Codes Demo
// @Produce      json
// @Param        code  query  int  false  "2xx status code to demo"  Enums(200, 201, 202, 204, 206)
// @Success      200   {object}  models.SuccessResponse  "OK"
// @Success      201   {object}  models.SuccessResponse  "Created"
// @Success      202   {object}  models.SuccessResponse  "Accepted"
// @Success      204   "No Content"
// @Success      206   {object}  models.SuccessResponse  "Partial Content"
// @Router       /demo/status/2xx [get]
func Demo2xx(c *gin.Context) {
	codeStr := c.DefaultQuery("code", "200")

	type demo struct {
		code    int
		message string
		data    interface{}
	}

	demos := map[string]demo{
		"200": {200, "OK - Request successful, data returned", map[string]string{"result": "Full data"}},
		"201": {201, "Created - Resource created successfully", map[string]string{"id": "42", "created": "true"}},
		"202": {202, "Accepted - Request received but not yet processed (async)", map[string]string{"task_id": "abc-123", "status": "processing"}},
		"204": {204, "", nil},
		"206": {206, "Partial Content - Returning a portion of data (Range request)", map[string]string{"range": "bytes 0-1023/5120"}},
	}

	d, ok := demos[codeStr]
	if !ok {
		d = demos["200"]
	}

	if d.code == 204 {
		c.Status(http.StatusNoContent)
		return
	}

	c.JSON(d.code, models.SuccessResponse{
		Code:    d.code,
		Message: d.message,
		Data:    d.data,
	})
}

// Demo3xx godoc
// @Summary      Demo 3xx status codes - Redirection
// @Description  Demonstrates redirect codes: 301 Moved Permanently, 302 Found, 304 Not Modified, 307 Temporary Redirect, 308 Permanent Redirect.
// @Tags         HTTP Status Codes Demo
// @Produce      json
// @Param        code  query  int  false  "3xx status code to demo"  Enums(301, 302, 304, 307, 308)
// @Success      301   {object}  models.SuccessResponse  "Moved Permanently"
// @Success      302   {object}  models.SuccessResponse  "Found (Temporary Redirect)"
// @Success      304   "Not Modified"
// @Success      307   {object}  models.SuccessResponse  "Temporary Redirect"
// @Success      308   {object}  models.SuccessResponse  "Permanent Redirect"
// @Router       /demo/status/3xx [get]
func Demo3xx(c *gin.Context) {
	codeStr := c.DefaultQuery("code", "301")

	type info struct {
		code        int
		message     string
		location    string
		description string
	}

	demos := map[string]info{
		"301": {301, "Moved Permanently", "https://new-domain.example.com/users", "Resource has permanently moved to a new URL"},
		"302": {302, "Found", "https://temp-location.example.com/users", "Temporary redirect, method may change to GET"},
		"304": {304, "Not Modified", "", "Resource has not changed, use cached version"},
		"307": {307, "Temporary Redirect", "https://temp-location.example.com/users", "Temporary redirect, original HTTP method preserved"},
		"308": {308, "Permanent Redirect", "https://new-domain.example.com/users", "Permanent redirect, original HTTP method preserved"},
	}

	d, ok := demos[codeStr]
	if !ok {
		d = demos["301"]
	}

	if d.code == 304 {
		c.Status(http.StatusNotModified)
		return
	}

	c.Header("Location", d.location)
	c.JSON(d.code, models.SuccessResponse{
		Code:    d.code,
		Message: d.message,
		Data: map[string]string{
			"description":  d.description,
			"redirect_url": d.location,
			"note":         "Header 'Location' has been set",
		},
	})
}

// Demo4xx godoc
// @Summary      Demo 4xx status codes - Client Error
// @Description  Demonstrates client-side errors: 400, 401, 403, 404, 405, 408, 409, 410, 422, 429.
// @Tags         HTTP Status Codes Demo
// @Produce      json
// @Param        code  query  int  false  "4xx status code to demo"  Enums(400, 401, 403, 404, 405, 408, 409, 410, 422, 429)
// @Failure      400   {object}  models.ErrorResponse  "Bad Request"
// @Failure      401   {object}  models.ErrorResponse  "Unauthorized"
// @Failure      403   {object}  models.ErrorResponse  "Forbidden"
// @Failure      404   {object}  models.ErrorResponse  "Not Found"
// @Failure      405   {object}  models.ErrorResponse  "Method Not Allowed"
// @Failure      408   {object}  models.ErrorResponse  "Request Timeout"
// @Failure      409   {object}  models.ErrorResponse  "Conflict"
// @Failure      410   {object}  models.ErrorResponse  "Gone"
// @Failure      422   {object}  models.ErrorResponse  "Unprocessable Entity"
// @Failure      429   {object}  models.ErrorResponse  "Too Many Requests"
// @Router       /demo/status/4xx [get]
func Demo4xx(c *gin.Context) {
	codeStr := c.DefaultQuery("code", "400")

	type errInfo struct {
		code    int
		message string
		detail  string
	}

	demos := map[string]errInfo{
		"400": {400, "Bad Request", "Request has malformed syntax or invalid parameters"},
		"401": {401, "Unauthorized", "Not authenticated. A valid token (Bearer token) must be provided"},
		"403": {403, "Forbidden", "Authenticated but not authorized to access this resource"},
		"404": {404, "Not Found", "Resource does not exist on the server"},
		"405": {405, "Method Not Allowed", "HTTP method is not supported for this endpoint"},
		"408": {408, "Request Timeout", "Client sent the request too slowly; server timed out"},
		"409": {409, "Conflict", "Request conflicts with the current state of the server (e.g. duplicate email)"},
		"410": {410, "Gone", "Resource has been permanently deleted and no longer exists"},
		"422": {422, "Unprocessable Entity", "Syntax is correct but data cannot be processed (validation error)"},
		"429": {429, "Too Many Requests", "Too many requests sent in a short period (rate limiting)"},
	}

	d, ok := demos[codeStr]
	if !ok {
		d = demos["400"]
	}

	if d.code == 429 {
		c.Header("Retry-After", "60")
	}
	if d.code == 405 {
		c.Header("Allow", "GET, POST")
	}

	c.JSON(d.code, models.ErrorResponse{
		Code:    d.code,
		Message: d.message,
		Detail:  d.detail,
	})
}

// Demo5xx godoc
// @Summary      Demo 5xx status codes - Server Error
// @Description  Demonstrates server-side errors: 500, 501, 502, 503, 504, 507.
// @Tags         HTTP Status Codes Demo
// @Produce      json
// @Param        code  query  int  false  "5xx status code to demo"  Enums(500, 501, 502, 503, 504, 507)
// @Failure      500   {object}  models.ErrorResponse  "Internal Server Error"
// @Failure      501   {object}  models.ErrorResponse  "Not Implemented"
// @Failure      502   {object}  models.ErrorResponse  "Bad Gateway"
// @Failure      503   {object}  models.ErrorResponse  "Service Unavailable"
// @Failure      504   {object}  models.ErrorResponse  "Gateway Timeout"
// @Failure      507   {object}  models.ErrorResponse  "Insufficient Storage"
// @Router       /demo/status/5xx [get]
func Demo5xx(c *gin.Context) {
	codeStr := c.DefaultQuery("code", "500")

	type errInfo struct {
		code    int
		message string
		detail  string
	}

	demos := map[string]errInfo{
		"500": {500, "Internal Server Error", "Server encountered an unknown error and could not complete the request"},
		"501": {501, "Not Implemented", "This feature has not been implemented on the server"},
		"502": {502, "Bad Gateway", "Server received an invalid response from the upstream server"},
		"503": {503, "Service Unavailable", "Server is overloaded or under maintenance, please try again later"},
		"504": {504, "Gateway Timeout", "Upstream server did not respond in time"},
		"507": {507, "Insufficient Storage", "Server does not have enough storage to complete the request"},
	}

	d, ok := demos[codeStr]
	if !ok {
		d = demos["500"]
	}

	if d.code == 503 {
		c.Header("Retry-After", "120")
	}

	c.JSON(d.code, models.ErrorResponse{
		Code:    d.code,
		Message: d.message,
		Detail:  d.detail,
	})
}
