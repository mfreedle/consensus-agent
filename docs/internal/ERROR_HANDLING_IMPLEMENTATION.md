# Error Handling and Loading States Implementation Guide

## Overview

The Consensus Agent app now features a comprehensive, production-ready error handling and loading state system that provides:

- **Global Error Boundaries**: Catch and gracefully handle uncaught React errors
- **Centralized Error Management**: Unified error state management with context
- **User-Friendly Notifications**: Toast-based error messages with actions
- **Enhanced API Service**: Robust API calls with retry logic and typed errors
- **Loading Indicators**: Flexible loading states for better UX

## Architecture

### Core Components

1. **ErrorBoundary** (`src/components/ErrorBoundary.tsx`)
   - Catches uncaught React errors
   - Provides fallback UI with error details
   - Includes reload functionality

2. **ErrorContext** (`src/contexts/ErrorContext.tsx`)
   - Centralized error state management
   - Toast notification system
   - Auto-expiring error messages

3. **Enhanced API Service** (`src/services/enhancedApi.ts`)
   - Typed error handling
   - Automatic retry logic
   - Request/response interceptors
   - Timeout management

4. **Loading Indicators** (`src/components/LoadingIndicator.tsx`)
   - Multiple variants (overlay, inline, skeleton)
   - Configurable sizes and messages
   - Progress tracking support

### Hooks

1. **useErrorHandler** (`src/hooks/useErrorHandler.ts`)
   - Simplified error reporting
   - Error categorization
   - Action suggestions

## Usage Examples

### Basic Error Handling in Components

```tsx
import { useErrorHandler } from '../hooks/useErrorHandler';
import { enhancedApiService } from '../services/enhancedApi';

const MyComponent: React.FC = () => {
  const { addError } = useErrorHandler();
  const [isLoading, setIsLoading] = useState(false);

  const handleApiCall = async () => {
    try {
      setIsLoading(true);
      const result = await enhancedApiService.request('/api/data');
      // Handle success
    } catch (error) {
      addError(error, 'api', 'Failed to fetch data');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      {isLoading && <LoadingIndicator isLoading={true} message="Loading..." />}
      <button onClick={handleApiCall}>Fetch Data</button>
    </div>
  );
};
```

### File Upload with Progress and Error Handling

```tsx
const uploadFile = useCallback(async (file: File) => {
  try {
    setIsUploading(true);
    setUploadProgress(0);
    
    await enhancedApiService.uploadFile(file, (progress) => {
      setUploadProgress(progress);
    });
    
    // Success handling
  } catch (error) {
    addError(error, 'upload', `Failed to upload ${file.name}`);
  } finally {
    setIsUploading(false);
    setUploadProgress(0);
  }
}, [addError]);
```

### Loading States with Different Variants

```tsx
// Overlay loading (full screen)
<LoadingIndicator 
  isLoading={true} 
  variant="overlay" 
  message="Processing your request..." 
/>

// Inline loading (within content)
<LoadingIndicator 
  isLoading={true} 
  variant="inline" 
  size="sm"
  message="Saving..." 
/>

// Skeleton loading (placeholder content)
<LoadingIndicator 
  isLoading={true} 
  variant="skeleton" 
  className="h-32" 
/>
```

## Error Categories

The system categorizes errors for better handling:

- **network**: Connection issues, timeouts
- **validation**: Input validation errors
- **auth**: Authentication/authorization errors
- **upload**: File upload specific errors
- **api**: General API errors
- **unknown**: Uncategorized errors

## Migration Guide

### From Old API Service

Replace `apiService` calls with `enhancedApiService`:

```tsx
// Before
const result = await apiService.getData();
if (result.error) {
  // Handle error
}

// After
try {
  const result = await enhancedApiService.getData();
  // Handle success
} catch (error) {
  addError(error, 'api', 'Failed to get data');
}
```

### From Manual Error States

Replace local error state with global error handling:

```tsx
// Before
const [error, setError] = useState<string | null>(null);
setError('Something went wrong');

// After
const { addError } = useErrorHandler();
addError(new Error('Something went wrong'), 'api', 'Operation failed');
```

## Best Practices

1. **Always use try-catch** for async operations
2. **Categorize errors** appropriately for better UX
3. **Provide meaningful context** in error messages
4. **Use loading indicators** for operations > 200ms
5. **Clear errors** when appropriate (e.g., on successful retry)
6. **Test error scenarios** during development

## Enhanced API Service Features

### Automatic Retries

```tsx
const result = await enhancedApiService.request('/api/data', {
  retries: 3, // Will retry up to 3 times
  timeout: 10000 // 10 second timeout
});
```

### Safe Requests (Legacy Compatibility)

```tsx
const result = await enhancedApiService.safeRequest('/api/data');
if (result.error) {
  // Handle error
} else {
  // Handle success with result.data
}
```

### File Upload with Progress

```tsx
await enhancedApiService.uploadFile(file, (progress) => {
  console.log(`Upload progress: ${progress}%`);
});
```

## Refactored Components

The following components have been updated to use the new system:

- **FileUpload**: Global error handling, loading overlays, file validation
- **FileList**: Enhanced loading states, error toasts for deletion
- **ChatInterface**: Better message sending UX, error feedback
- **ModelSelection**: Improved model loading, error handling

## Testing

Run the error handling test suite:

```bash
cd frontend
npm test test/errorHandling.test.ts
```

## Future Enhancements

- Error analytics and reporting
- Offline error queuing
- Custom error recovery actions
- More granular loading states
- Performance monitoring integration

## Troubleshooting

### Common Issues

1. **Errors not showing**: Ensure components are wrapped in ErrorProvider
2. **Loading not working**: Check LoadingIndicator props and state
3. **API errors**: Verify enhanced API service configuration
4. **Toast not dismissing**: Check auto-expire settings

### Debug Mode

Enable detailed error logging:

```tsx
const { addError } = useErrorHandler();
addError(error, 'api', 'Debug message', { debug: true });
```

## Contributing

When adding new features:

1. Use the error handling hooks consistently
2. Add appropriate loading states
3. Test error scenarios
4. Update documentation
5. Follow the established patterns

---

This error handling system provides a solid foundation for production-ready error management and user experience improvements in the Consensus Agent application.
