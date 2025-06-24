# Error Code Standardization Guidelines

## 🎯 **Error Code Strategy**

### **Core Principle: Semantic Error Codes**
- **Use semantic error codes for client-distinguishable errors**
- **Use class name defaults for generic domain errors**
- **Never use empty string error codes**

### **When to Use Custom Error Codes**

#### ✅ **Client Applications Need Different Handling**
```python
# Authentication - clients need to distinguish token vs credentials
class InvalidTokenError(AuthenticationError):
    def __init__(self):
        super().__init__(
            "Authentication token is invalid or expired",
            error_code="INVALID_TOKEN"
        )

class InvalidCredentialsError(AuthenticationError):
    def __init__(self):
        super().__init__(
            "Invalid email or password",
            error_code="INVALID_CREDENTIALS"
        )
```

#### ✅ **Business Rules with Specific Actions**
```python
# User registration - different error codes for different validation failures
class EmailAlreadyExistsError(ConflictError):
    def __init__(self, email: str):
        super().__init__(
            f"An account with email '{email}' already exists",
            error_code="EMAIL_ALREADY_EXISTS"
        )

class UsernameAlreadyExistsError(ConflictError):
    def __init__(self, username: str):
        super().__init__(
            f"Username '{username}' is already taken",
            error_code="USERNAME_ALREADY_EXISTS"
        )
```

### **When to Use Default Error Codes (Class Names)**

#### ✅ **Generic Domain Errors**
```python
# Simple not found cases - class name is sufficient
class ArticleNotFoundError(NotFoundError):
    def __init__(self, message: str):
        super().__init__(message)  # error_code defaults to "ArticleNotFoundError"

class UserNotFoundError(NotFoundError):
    def __init__(self, message: str):
        super().__init__(message)  # error_code defaults to "UserNotFoundError"
```

#### ✅ **Permission Errors**
```python
# Permission errors - class name provides enough context
class ArticlePermissionError(PermissionError):
    def __init__(self, message: str):
        super().__init__(message)  # error_code defaults to "ArticlePermissionError"
```

### **❌ Never Use These Patterns**

```python
# ❌ WRONG: Empty string error codes
raise AuthenticationError("Invalid token", error_code="")

# ❌ WRONG: Generic error codes that don't add value
raise UserNotFoundError("User not found", error_code="NOT_FOUND")

# ❌ WRONG: Overly verbose error codes
raise ValidationError("Invalid email", error_code="INVALID_EMAIL_FORMAT_VALIDATION_ERROR")
```

## 🔧 **Implementation Rules**

### **Default Behavior (Recommended)**
```python
# Let the base class generate error_code from class name
class ArticleNotFoundError(NotFoundError):
    def __init__(self, message: str):
        super().__init__(message)  # error_code = "ArticleNotFoundError"
```

### **Custom Error Codes (When Needed)**
```python
# Provide semantic error codes for client distinction
class InvalidTokenError(AuthenticationError):
    def __init__(self):
        super().__init__(
            "Authentication token is invalid or expired",
            error_code="INVALID_TOKEN"
        )
```

### **Error Code Naming Convention**
- Use `SCREAMING_SNAKE_CASE`
- Be concise but descriptive
- Focus on the **why** not the **what**
- Group related errors with prefixes when helpful

**Examples:**
- `INVALID_TOKEN` (not `AUTHENTICATION_TOKEN_INVALID`)
- `EMAIL_ALREADY_EXISTS` (not `DUPLICATE_EMAIL_ERROR`)
- `INSUFFICIENT_PERMISSIONS` (not `PERMISSION_DENIED`)

## 📋 **Error Code Categories**

### **Authentication & Authorization**
- `INVALID_TOKEN` - Token is malformed, expired, or invalid
- `MISSING_TOKEN` - No authentication provided
- `INVALID_CREDENTIALS` - Email/password combination incorrect
- `INSUFFICIENT_PERMISSIONS` - User lacks required permissions

### **Resource Conflicts**
- `EMAIL_ALREADY_EXISTS` - Email already registered
- `USERNAME_ALREADY_EXISTS` - Username already taken
- `SLUG_ALREADY_EXISTS` - Article slug already in use

### **Validation Errors**
- `INVALID_EMAIL_FORMAT` - Email format is invalid
- `WEAK_PASSWORD` - Password doesn't meet requirements
- `CANNOT_FOLLOW_SELF` - User trying to follow themselves

### **Default Class Names (Most Common)**
- `UserNotFoundError` - Generic user not found
- `ArticleNotFoundError` - Generic article not found
- `CommentNotFoundError` - Generic comment not found
- `ProfileNotFoundError` - Generic profile not found
- `ArticlePermissionError` - Generic article permission issue
- `CommentPermissionError` - Generic comment permission issue
