import ReactGA from 'react-ga4';

// Initialize Google Analytics 4
const initializeGA = () => {
  const measurementId = process.env.REACT_APP_GA_MEASUREMENT_ID;
  
  if (measurementId) {
    ReactGA.initialize(measurementId, {
      gtagOptions: {
        anonymize_ip: true,
        cookie_flags: 'secure;samesite=strict'
      }
    });
    
    console.log('🎯 Analytics initialized with ID:', measurementId);
  } else {
    console.warn('⚠️ GA Measurement ID not found in environment variables');
  }
};

// === PAGE TRACKING ===

export const trackPageView = (path, title = '') => {
  ReactGA.send({ 
    hitType: 'pageview', 
    page: path,
    title: title
  });
};

// === USER JOURNEY TRACKING ===

export const trackLandingView = (userType = 'visitor') => {
  ReactGA.event('landing_page_view', {
    user_type: userType,
    method: 'organic'
  });
};

export const trackSignup = (userType, method = 'email') => {
  ReactGA.event('sign_up', {
    method: method,
    user_type: userType
  });
  
  // Set user properties
  ReactGA.set({ user_type: userType });
};

export const trackLogin = (userType) => {
  ReactGA.event('login', {
    method: 'email',
    user_type: userType
  });
  
  ReactGA.set({ user_type: userType });
};

// === BUSINESS EVENTS ===

export const trackServiceBrowse = (category, resultsCount = 0) => {
  ReactGA.event('browse_services', {
    category: category,
    results_count: resultsCount
  });
};

export const trackQuotationRequest = (providerId, serviceType, estimatedValue = null) => {
  const params = {
    provider_id: providerId,
    service_type: serviceType,
    funnel_step: 'quotation_request'
  };
  
  if (estimatedValue) {
    params.value = estimatedValue;
    params.currency = 'USD';
  }
  
  ReactGA.event('quotation_request', params);
};

export const trackProviderProfileView = (providerId, userType = 'homeowner') => {
  ReactGA.event('provider_profile_view', {
    provider_id: providerId,
    user_type: userType
  });
};

export const trackMessageSent = (recipientType) => {
  ReactGA.event('message_sent', {
    recipient_type: recipientType,
    message_type: 'text'
  });
};

export const trackReviewSubmitted = (providerId, rating) => {
  ReactGA.event('review_submitted', {
    provider_id: providerId,
    rating: rating
  });
};

// === PROVIDER EVENTS ===

export const trackQuotationSent = (quotationId, amount) => {
  ReactGA.event('quotation_sent', {
    quotation_id: quotationId,
    value: amount,
    currency: 'USD',
    funnel_step: 'quotation_sent'
  });
};

export const trackDashboardView = (userType, metrics = {}) => {
  ReactGA.event('dashboard_view', {
    dashboard_type: `${userType}_dashboard`,
    ...metrics
  });
};

export const trackAnalyticsView = (timePeriod = 'weekly') => {
  ReactGA.event('analytics_view', {
    time_period: timePeriod,
    dashboard_type: 'provider_analytics'
  });
};

// === SEARCH TRACKING ===

export const trackSearch = (query, resultsCount, location = null) => {
  const params = {
    search_query: query,
    results_count: resultsCount
  };
  
  if (location) {
    params.location = location;
  }
  
  ReactGA.event('search', params);
};

// === CONVERSION TRACKING ===

export const trackBookingRequest = (providerId, serviceType, amount) => {
  ReactGA.event('booking_request', {
    provider_id: providerId,
    service_type: serviceType,
    value: amount,
    currency: 'USD',
    funnel_step: 'booking_request'
  });
};

export const trackFirstBooking = (bookingId, providerId, amount, serviceType) => {
  ReactGA.event('first_booking', {
    booking_id: bookingId,
    provider_id: providerId,
    value: amount,
    currency: 'USD',
    service_type: serviceType,
    funnel_step: 'booking_confirmed'
  });
};

export const trackRepeatBooking = (bookingId, providerId, amount, serviceType, bookingCount) => {
  ReactGA.event('repeat_booking', {
    booking_id: bookingId,
    provider_id: providerId,
    value: amount,
    currency: 'USD',
    service_type: serviceType,
    booking_count: bookingCount,
    funnel_step: 'booking_confirmed'
  });
};

// === ERROR TRACKING ===

export const trackError = (errorType, errorMessage, page) => {
  ReactGA.event('error_occurred', {
    error_type: errorType,
    error_message: errorMessage,
    page: page
  });
};

// === ENGAGEMENT TRACKING ===

export const trackButtonClick = (buttonName, location) => {
  ReactGA.event('button_click', {
    button_name: buttonName,
    location: location
  });
};

export const trackFormSubmit = (formType, success = true) => {
  ReactGA.event('form_submit', {
    form_type: formType,
    success: success
  });
};

export const trackFileUpload = (fileType, fileSize) => {
  ReactGA.event('file_upload', {
    file_type: fileType,
    file_size: fileSize
  });
};

// === TIMING TRACKING ===

export const trackTiming = (category, variable, value) => {
  ReactGA.gtag('event', 'timing_complete', {
    name: variable,
    value: value,
    event_category: category
  });
};

// === USER PROPERTIES ===

export const setUserProperties = (properties) => {
  ReactGA.set(properties);
};

export const setUserId = (userId) => {
  ReactGA.set({ user_id: userId });
};

// === CUSTOM DIMENSIONS ===

export const trackCustomEvent = (eventName, parameters) => {
  ReactGA.event(eventName, parameters);
};

// Initialize analytics when module is imported
initializeGA();

// Export the analytics functions
export default {
  initializeGA,
  trackPageView,
  trackLandingView,
  trackSignup,
  trackLogin,
  trackServiceBrowse,
  trackQuotationRequest,
  trackProviderProfileView,
  trackMessageSent,
  trackReviewSubmitted,
  trackQuotationSent,
  trackDashboardView,
  trackAnalyticsView,
  trackSearch,
  trackBookingRequest,
  trackFirstBooking,
  trackRepeatBooking,
  trackError,
  trackButtonClick,
  trackFormSubmit,
  trackFileUpload,
  trackTiming,
  setUserProperties,
  setUserId,
  trackCustomEvent
};