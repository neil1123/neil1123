import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiService from '../../services/api';
import { 
  BarChart3, 
  TrendingUp,
  DollarSign,
  Clock,
  Star,
  Plus,
  Bell,
  LogOut,
  MessageSquare,
  Users,
  Menu,
  X,
  Calendar
} from 'lucide-react';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Avatar, AvatarFallback } from '../../components/ui/avatar';
import NotificationBadge from '../../components/NotificationBadge';
import ProviderAnalyticsDashboard from '../../components/ProviderAnalyticsDashboard';
import { STANDARD_PROVIDER_SIDEBAR, handleStandardLogout } from '../../constants/providerSidebarConfig';

const ProviderDashboard = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('home');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  
  // Mock notification state - in real app this would come from API/context
  const [notifications] = useState({
    totalUnreadMessages: 0,
    newOrders: 0,
    quotationRequests: 0
  });

  const handleLogout = () => {
    handleStandardLogout(navigate);
  };

  const sidebarItems = STANDARD_PROVIDER_SIDEBAR;

  // Empty states for fresh platform - no activities for new users
  const recentActivity = [];

  // User profile state - fetch from database
  const [userProfile, setUserProfile] = useState(null);
  const [userInitials, setUserInitials] = useState('U');
  const [dashboardData, setDashboardData] = useState({
    totalRevenue: 0,
    activeJobs: 0,
    customerRating: 5.0,
    weeklyRevenue: 0
  });

  // Load user profile on component mount
  useEffect(() => {
    loadUserProfile();
    loadDashboardData();
  }, []);

  const loadUserProfile = async () => {
    try {
      const profile = await apiService.getUserProfile();
      setUserProfile(profile);
      
      // Set user initials from actual database data
      const initials = profile.name 
        ? profile.name.split(' ').map(name => name[0]).join('').toUpperCase() 
        : 'U';
      setUserInitials(initials);
      
      console.log('User profile loaded:', profile);
    } catch (error) {
      console.error('Failed to load user profile:', error);
      // Fallback to localStorage if API fails
      const fallbackUser = JSON.parse(localStorage.getItem('user') || '{}');
      if (fallbackUser.name) {
        const initials = fallbackUser.name.split(' ').map(name => name[0]).join('').toUpperCase();
        setUserInitials(initials);
      }
    }
  };

  const loadDashboardData = async () => {
    try {
      // Load orders to calculate total revenue and active jobs
      const orders = await apiService.getOrders();
      
      const completedOrders = orders.filter(order => order.status === 'completed');
      const activeOrders = orders.filter(order => 
        ['accepted', 'in_progress'].includes(order.status)
      );
      
      const totalRevenue = completedOrders.reduce((sum, order) => 
        sum + (parseFloat(order.quotation_amount) || 0), 0
      );
      
      // Calculate weekly revenue
      const oneWeekAgo = new Date();
      oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
      
      const weeklyRevenue = completedOrders
        .filter(order => new Date(order.request_date) >= oneWeekAgo)
        .reduce((sum, order) => sum + (parseFloat(order.quotation_amount) || 0), 0);
      
      setDashboardData({
        totalRevenue,
        activeJobs: activeOrders.length,
        customerRating: userProfile?.rating || 5.0,
        weeklyRevenue
      });
      
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Mobile Menu Button - Only show on mobile */}
            <div className="flex items-center space-x-4">
              <Button 
                variant="ghost" 
                size="sm" 
                className="flex items-center xl:hidden"
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              >
                {isMobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </Button>
              <h1 className="text-2xl font-bold text-blue-600">Doord.</h1>
              <span className="text-sm text-gray-600 hidden sm:inline">for Merchants</span>
            </div>
            
            {/* Desktop Right Side */}
            <div className="hidden xl:flex items-center space-x-4">
              <Button variant="ghost" size="sm">
                <Bell className="h-4 w-4" />
                {notifications.totalUnreadMessages > 0 && (
                  <NotificationBadge count={notifications.totalUnreadMessages} className="ml-1" />
                )}
              </Button>
              <div className="flex items-center space-x-2">
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => navigate('/homeservices/settings')}
                  className="p-1"
                >
                  <Avatar className="h-8 w-8">
                    <AvatarFallback className="bg-blue-100 text-blue-600">
                      {userInitials}
                    </AvatarFallback>
                  </Avatar>
                </Button>
                <span className="text-sm font-medium">{userProfile?.business_name || userProfile?.name || 'User'}</span>
              </div>
              <Button variant="ghost" size="sm" onClick={handleLogout} title="Logout">
                <LogOut className="h-4 w-4" />
              </Button>
            </div>

            {/* Mobile Right Side */}
            <div className="xl:hidden flex items-center space-x-2">
              <Button variant="ghost" size="sm">
                <Bell className="h-4 w-4" />
                {notifications.totalUnreadMessages > 0 && (
                  <NotificationBadge count={notifications.totalUnreadMessages} className="ml-1" />
                )}
              </Button>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => navigate('/homeservices/settings')}
                className="p-1"
              >
                <Avatar className="h-8 w-8">
                  <AvatarFallback className="bg-blue-100 text-blue-600">
                    {userInitials}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile Navigation Overlay - Only show on mobile */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-50 xl:hidden">
          <div className="fixed inset-0 bg-black bg-opacity-50" onClick={() => setIsMobileMenuOpen(false)} />
          <div className="fixed top-0 left-0 w-64 h-full bg-white shadow-lg">
            <div className="p-4">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">Navigation</h2>
                <Button variant="ghost" size="sm" onClick={() => setIsMobileMenuOpen(false)}>
                  <X className="h-5 w-5" />
                </Button>
              </div>
              <nav className="space-y-2">
                {sidebarItems.map((item) => (
                  <Button
                    key={item.id}
                    variant={activeTab === item.id ? "default" : "ghost"}
                    className="w-full justify-start"
                    onClick={() => {
                      setActiveTab(item.id);
                      navigate(item.path);
                      setIsMobileMenuOpen(false);
                    }}
                  >
                    <item.icon className="h-4 w-4 mr-3" />
                    {item.label}
                  </Button>
                ))}
                <hr className="my-4" />
                <Button
                  variant="ghost"
                  className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
                  onClick={handleLogout}
                >
                  <LogOut className="h-4 w-4 mr-3" />
                  Logout
                </Button>
              </nav>
            </div>
          </div>
        </div>
      )}

      <div className="flex">
        {/* Desktop Sidebar - Always show on desktop like homeowner explore */}
        <div className="hidden xl:block w-64 bg-white shadow-sm min-h-screen">
          <div className="p-4">
            <div className="mb-6">
              <h1 className="text-2xl font-bold text-blue-600">Doord.</h1>
            </div>
            <nav className="space-y-2">
              {sidebarItems.map((item) => (
                <Button
                  key={item.id}
                  variant={activeTab === item.id ? "default" : "ghost"}
                  className="w-full justify-start"
                  onClick={() => {
                    setActiveTab(item.id);
                    navigate(item.path);
                  }}
                >
                  <item.icon className="h-4 w-4 mr-3" />
                  {item.label}
                </Button>
              ))}
              <hr className="my-4" />
              <Button
                variant="ghost"
                className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
                onClick={handleLogout}
              >
                <LogOut className="h-4 w-4 mr-3" />
                Logout
              </Button>
            </nav>
          </div>
        </div>

        {/* Main Content - Adjust width for desktop sidebar */}
        <div className="flex-1 xl:pl-0 p-4 md:p-8">
          <div className="max-w-7xl mx-auto">
            {/* Dashboard Header */}
            <div className="mb-8">
              <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">Dashboard</h2>
              <p className="text-gray-600">Welcome back! Here's what's happening with your business.</p>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              <Card 
                className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => navigate('/homeservices/analytics')}
              >
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Total Revenue</p>
                      <p className="text-2xl font-bold text-gray-900">${dashboardData.totalRevenue.toFixed(2)}</p>
                    </div>
                    <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <DollarSign className="h-4 w-4 text-blue-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card 
                className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => navigate('/homeservices/orders?tab=confirmed')}
              >
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Active Jobs</p>
                      <p className="text-2xl font-bold text-gray-900">{dashboardData.activeJobs}</p>
                    </div>
                    <div className="h-8 w-8 bg-green-100 rounded-full flex items-center justify-center">
                      <Clock className="h-4 w-4 text-green-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Customer Rating</p>
                      <p className="text-2xl font-bold text-gray-900">{dashboardData.customerRating.toFixed(1)}</p>
                    </div>
                    <div className="h-8 w-8 bg-yellow-100 rounded-full flex items-center justify-center">
                      <Star className="h-4 w-4 text-yellow-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card 
                className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => navigate('/homeservices/profile')}
              >
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">View your Profile</p>
                      <p className="text-2xl font-bold text-gray-900">Company</p>
                    </div>
                    <div className="h-8 w-8 bg-purple-100 rounded-full flex items-center justify-center">
                      <TrendingUp className="h-4 w-4 text-purple-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Charts and Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              {/* Weekly Performance Chart */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <BarChart3 className="h-5 w-5 mr-2" />
                    Weekly Performance
                  </CardTitle>
                </CardHeader>
                <CardContent className="px-4 py-6">
                  <div className="h-48 md:h-64">
                    <div className="text-center py-8 text-gray-500">
                      <BarChart3 className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                      <p>Weekly performance tracking</p>
                      <p className="text-sm">Complete more orders to see detailed analytics</p>
                      <div className="mt-4 text-left">
                        <div className="bg-blue-50 p-3 rounded-lg">
                          <p className="text-sm font-medium text-blue-900">This Week's Revenue</p>
                          <p className="text-2xl font-bold text-blue-600">${dashboardData.weeklyRevenue.toFixed(2)}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Upcoming Activity */}
              <Card className="mt-6 lg:mt-0">
                <CardHeader>
                  <CardTitle>Upcoming Activity</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {recentActivity.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">
                        <Calendar className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                        <p>No upcoming appointments or orders</p>
                        <p className="text-sm">Schedule new work to see your upcoming activities</p>
                      </div>
                    ) : (
                      recentActivity.map((activity) => (
                        <div key={activity.id} className="flex items-start space-x-3">
                          <div className="h-2 w-2 bg-blue-600 rounded-full mt-2 flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900">{activity.message}</p>
                            <p className="text-xs text-gray-500">{activity.time}</p>
                          </div>
                          <Badge variant={activity.status === 'pending' ? 'secondary' : 'default'}>
                            {activity.status}
                          </Badge>
                        </div>
                      ))
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <Card 
                className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => window.location.href = '/homeservices/orders'}
              >
                <CardContent className="p-6">
                  <div className="flex items-center space-x-4">
                    <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <Plus className="h-6 w-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">New Order</h3>
                      <p className="text-sm text-gray-600">Create a new service order</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card 
                className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => window.location.href = '/homeservices/messages'}
              >
                <CardContent className="p-6">
                  <div className="flex items-center space-x-4">
                    <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center">
                      <MessageSquare className="h-6 w-6 text-green-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">Messages</h3>
                      <p className="text-sm text-gray-600">Check customer messages</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card 
                className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => window.location.href = '/homeservices/customers'}
              >
                <CardContent className="p-6">
                  <div className="flex items-center space-x-4">
                    <div className="h-12 w-12 bg-purple-100 rounded-full flex items-center justify-center">
                      <Users className="h-6 w-6 text-purple-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">Customers</h3>
                      <p className="text-sm text-gray-600">Manage customer relationships</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProviderDashboard;