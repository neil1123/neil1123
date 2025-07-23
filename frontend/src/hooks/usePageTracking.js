import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { trackPageView } from '../services/analytics';

/**
 * Hook to automatically track page views when route changes
 * Add this to your main App.js component
 */
const usePageTracking = () => {
  const location = useLocation();

  useEffect(() => {
    // Track page view on route change
    trackPageView(location.pathname + location.search, getPageTitle(location.pathname));
  }, [location]);

  // Helper function to get page titles
  const getPageTitle = (pathname) => {
    const titles = {
      '/': 'Homepage',
      '/homeowners': 'Homeowner Landing',
      '/homeowners/browse': 'Browse Services',
      '/homeowners/auth': 'Homeowner Auth',
      '/homeowners/dashboard': 'Homeowner Dashboard',
      '/homeowners/quotations': 'My Quotations',
      '/homeservices': 'Provider Landing',
      '/homeservices/auth': 'Provider Auth',
      '/homeservices/dashboard': 'Provider Dashboard',
      '/homeservices/analytics': 'Provider Analytics',
      '/homeservices/orders': 'Provider Orders',
      '/homeservices/messages': 'Provider Messages',
      '/homeservices/profile': 'Company Profile',
      '/homeservices/settings': 'Provider Settings',
      '/homeservices/calendar': 'Provider Calendar',
      '/homeservices/customers': 'Provider Customers'
    };
    
    // Handle dynamic routes
    if (pathname.includes('/providers/')) {
      return 'Provider Profile';
    }
    
    return titles[pathname] || pathname;
  };
};

export default usePageTracking;