import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Mail, Lock, User, Phone, MapPin, Briefcase, Plus, X } from 'lucide-react';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Checkbox } from '../../components/ui/checkbox';
import { serviceCategories } from '../../data/mockData';
import apiService from '../../services/api';
import { trackSignup, trackLogin } from '../../services/analytics';

const ProviderAuth = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [availableServices, setAvailableServices] = useState([]);
  const [newService, setNewService] = useState('');
  const [showAddService, setShowAddService] = useState(false);
  
  // Sign In Form
  const [signInData, setSignInData] = useState({
    email: '',
    password: ''
  });
  
  // Sign Up Form
  const [signUpData, setSignUpData] = useState({
    businessName: '',
    ownerName: '',
    email: '',
    phone: '',
    address: '',
    services: [],
    password: '',
    confirmPassword: '',
    experience: '',
    license: ''
  });

  // Load available services on component mount
  useEffect(() => {
    loadAvailableServices();
  }, []);

  const loadAvailableServices = async () => {
    try {
      const services = await apiService.getAllServices();
      setAvailableServices(services);
    } catch (error) {
      console.error('Failed to load services:', error);
      // Fall back to default services if API fails
      const defaultServices = serviceCategories.flatMap(category => 
        category.services.map(service => service.name)
      );
      setAvailableServices(defaultServices);
    }
  };

  const handleSignIn = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    
    try {
      console.log('Attempting sign in with:', signInData.email);
      
      const response = await apiService.login({
        email: signInData.email,
        password: signInData.password
      });
      
      console.log('Login response:', response);
      
      // Check if user is a provider
      if (response.user.user_type !== 'provider') {
        throw new Error('This account is not registered as a service provider');
      }
      
      // Store user data
      localStorage.setItem('isLoggedIn', 'true');
      localStorage.setItem('userType', 'provider');
      localStorage.setItem('user', JSON.stringify(response.user));
      
      console.log('Redirecting to provider dashboard...');
      
      // Redirect to provider dashboard
      navigate('/homeservices/dashboard');
      
    } catch (error) {
      console.error('Sign in error:', error);
      setError(error.message || 'Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignUp = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    
    try {
      console.log('Sign up data:', signUpData);
      console.log('Services selected:', signUpData.services);
      
      // Validate form
      if (signUpData.password !== signUpData.confirmPassword) {
        throw new Error('Passwords do not match');
      }

      if (!signUpData.ownerName || !signUpData.email || !signUpData.businessName) {
        throw new Error('Please fill in all required fields');
      }

      if (signUpData.services.length === 0) {
        throw new Error('Please select at least one service');
      }

      // Prepare registration data
      const registrationData = {
        email: signUpData.email,
        password: signUpData.password,
        user_type: 'provider',
        name: signUpData.ownerName,
        phone: signUpData.phone,
        address: signUpData.address,
        business_name: signUpData.businessName,
        services: signUpData.services,
        license: signUpData.license,
        experience: signUpData.experience
      };

      console.log('Sending registration data:', registrationData);

      const response = await apiService.register(registrationData);
      
      console.log('Registration response:', response);
      
      // Store user data
      localStorage.setItem('isLoggedIn', 'true');
      localStorage.setItem('userType', 'provider');
      localStorage.setItem('user', JSON.stringify(response.user));
      
      console.log('Redirecting to provider dashboard...');
      
      // Redirect to dashboard
      navigate('/homeservices/dashboard');
      
    } catch (error) {
      console.error('Sign up error:', error);
      setError(error.message || 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleServiceToggle = (serviceName) => {
    console.log('Toggling service:', serviceName);
    console.log('Current services:', signUpData.services);
    
    setSignUpData(prev => {
      const newServices = prev.services.includes(serviceName)
        ? prev.services.filter(s => s !== serviceName)
        : [...prev.services, serviceName];
      
      console.log('New services:', newServices);
      
      return {
        ...prev,
        services: newServices
      };
    });
  };

  const handleAddNewService = () => {
    if (newService.trim() && !availableServices.includes(newService.trim())) {
      const trimmedService = newService.trim();
      setAvailableServices(prev => [...prev, trimmedService].sort());
      setSignUpData(prev => ({
        ...prev,
        services: [...prev.services, trimmedService]
      }));
      setNewService('');
      setShowAddService(false);
    }
  };

  const removeCustomService = (serviceName) => {
    // Remove from selected services
    setSignUpData(prev => ({
      ...prev,
      services: prev.services.filter(s => s !== serviceName)
    }));
    // Remove from available services (only if it's a custom added service)
    const isDefaultService = serviceCategories.flatMap(category => 
      category.services.map(service => service.name)
    ).includes(serviceName);
    
    if (!isDefaultService) {
      setAvailableServices(prev => prev.filter(s => s !== serviceName));
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <Button 
                variant="ghost" 
                onClick={() => navigate('/homeservices')}
                className="p-2"
              >
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <h1 className="text-2xl font-bold text-blue-600">Doord.</h1>
              <span className="text-sm text-gray-600">for Merchants</span>
            </div>
            <div className="text-sm text-gray-600">
              Homeowner? <Button variant="link" onClick={() => navigate('/homeowners/auth')}>Sign in here</Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-2xl mx-auto px-4 py-12">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Grow Your Business
          </h2>
          <p className="text-gray-600">
            Join the leading marketplace for home service providers
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-center text-xl">Service Provider Access</CardTitle>
          </CardHeader>
          <CardContent>
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            )}
            
            <Tabs defaultValue="signin" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="signin">Sign In</TabsTrigger>
                <TabsTrigger value="signup">Sign Up</TabsTrigger>
              </TabsList>
              
              <TabsContent value="signin">
                <form onSubmit={handleSignIn} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        id="email"
                        type="email"
                        placeholder="Enter your business email"
                        value={signInData.email}
                        onChange={(e) => setSignInData({...signInData, email: e.target.value})}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="password">Password</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        id="password"
                        type="password"
                        placeholder="Enter your password"
                        value={signInData.password}
                        onChange={(e) => setSignInData({...signInData, password: e.target.value})}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>
                  
                  <Button 
                    type="submit" 
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                    disabled={isLoading}
                  >
                    {isLoading ? 'Signing in...' : 'Sign In'}
                  </Button>
                  
                  <div className="text-center">
                    <Button variant="link" size="sm">
                      Forgot your password?
                    </Button>
                  </div>
                </form>
              </TabsContent>
              
              <TabsContent value="signup">
                <form onSubmit={handleSignUp} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="businessName">Business Name</Label>
                      <div className="relative">
                        <Briefcase className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                        <Input
                          id="businessName"
                          type="text"
                          placeholder="Your business name"
                          value={signUpData.businessName}
                          onChange={(e) => setSignUpData({...signUpData, businessName: e.target.value})}
                          className="pl-10"
                          required
                        />
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="ownerName">Owner Name</Label>
                      <div className="relative">
                        <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                        <Input
                          id="ownerName"
                          type="text"
                          placeholder="Your full name"
                          value={signUpData.ownerName}
                          onChange={(e) => setSignUpData({...signUpData, ownerName: e.target.value})}
                          className="pl-10"
                          required
                        />
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="email">Business Email</Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        id="email"
                        type="email"
                        placeholder="Enter your business email"
                        value={signUpData.email}
                        onChange={(e) => setSignUpData({...signUpData, email: e.target.value})}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="phone">Phone Number</Label>
                      <div className="relative">
                        <Phone className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                        <Input
                          id="phone"
                          type="tel"
                          placeholder="Business phone number"
                          value={signUpData.phone}
                          onChange={(e) => setSignUpData({...signUpData, phone: e.target.value})}
                          className="pl-10"
                          required
                        />
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="experience">Years of Experience</Label>
                      <Input
                        id="experience"
                        type="number"
                        placeholder="Years in business"
                        value={signUpData.experience}
                        onChange={(e) => setSignUpData({...signUpData, experience: e.target.value})}
                        required
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="address">Service Address</Label>
                    <div className="relative">
                      <MapPin className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        id="address"
                        type="text"
                        placeholder="Enter your business address"
                        value={signUpData.address}
                        onChange={(e) => setSignUpData({...signUpData, address: e.target.value})}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="license">License Number (Optional)</Label>
                    <Input
                      id="license"
                      type="text"
                      placeholder="Professional license number"
                      value={signUpData.license}
                      onChange={(e) => setSignUpData({...signUpData, license: e.target.value})}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label>Services Offered</Label>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => setShowAddService(true)}
                        className="text-xs"
                      >
                        <Plus className="h-3 w-3 mr-1" />
                        Add Service
                      </Button>
                    </div>
                    
                    {/* Add New Service Input */}
                    {showAddService && (
                      <div className="flex items-center space-x-2 p-2 bg-blue-50 rounded-md">
                        <Input
                          value={newService}
                          onChange={(e) => setNewService(e.target.value)}
                          placeholder="Enter new service name"
                          className="flex-1"
                          onKeyPress={(e) => {
                            if (e.key === 'Enter') {
                              e.preventDefault();
                              handleAddNewService();
                            }
                          }}
                        />
                        <Button
                          type="button"
                          size="sm"
                          onClick={handleAddNewService}
                          disabled={!newService.trim()}
                        >
                          Add
                        </Button>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setShowAddService(false);
                            setNewService('');
                          }}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    )}
                    
                    {/* Selected Services Tags */}
                    {signUpData.services.length > 0 && (
                      <div className="flex flex-wrap gap-2 p-2 bg-green-50 rounded-md">
                        {signUpData.services.map((service, index) => (
                          <div key={index} className="flex items-center bg-green-100 text-green-800 px-2 py-1 rounded-md text-xs">
                            <span>{service}</span>
                            <button
                              type="button"
                              onClick={() => removeCustomService(service)}
                              className="ml-1 text-green-600 hover:text-green-800"
                            >
                              <X className="h-3 w-3" />
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    <div className="grid grid-cols-2 gap-2 max-h-40 overflow-y-auto border rounded p-3">
                      {availableServices.map((serviceName, index) => (
                        <div key={index} className="flex items-center space-x-2">
                          <Checkbox
                            id={serviceName}
                            checked={signUpData.services.includes(serviceName)}
                            onCheckedChange={(checked) => {
                              console.log('Checkbox changed:', serviceName, 'checked:', checked);
                              if (checked) {
                                handleServiceToggle(serviceName);
                              } else {
                                handleServiceToggle(serviceName);
                              }
                            }}
                          />
                          <label
                            htmlFor={serviceName}
                            className="text-sm cursor-pointer"
                            onClick={() => {
                              console.log('Label clicked for:', serviceName);
                              handleServiceToggle(serviceName);
                            }}
                          >
                            {serviceName}
                          </label>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="password">Password</Label>
                      <div className="relative">
                        <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                        <Input
                          id="password"
                          type="password"
                          placeholder="Create a password"
                          value={signUpData.password}
                          onChange={(e) => setSignUpData({...signUpData, password: e.target.value})}
                          className="pl-10"
                          required
                        />
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="confirmPassword">Confirm Password</Label>
                      <div className="relative">
                        <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                        <Input
                          id="confirmPassword"
                          type="password"
                          placeholder="Confirm your password"
                          value={signUpData.confirmPassword}
                          onChange={(e) => setSignUpData({...signUpData, confirmPassword: e.target.value})}
                          className="pl-10"
                          required
                        />
                      </div>
                    </div>
                  </div>
                  
                  <Button
                    type="submit"
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                    disabled={
                      isLoading || 
                      !signUpData.businessName || 
                      !signUpData.ownerName || 
                      !signUpData.email || 
                      !signUpData.phone || 
                      !signUpData.address || 
                      !signUpData.password || 
                      !signUpData.confirmPassword ||
                      signUpData.password !== signUpData.confirmPassword || 
                      signUpData.services.length === 0
                    }
                    onClick={() => {
                      console.log('Submit button clicked');
                      console.log('Form validation state:', {
                        businessName: !!signUpData.businessName,
                        ownerName: !!signUpData.ownerName,
                        email: !!signUpData.email,
                        phone: !!signUpData.phone,
                        address: !!signUpData.address,
                        password: !!signUpData.password,
                        confirmPassword: !!signUpData.confirmPassword,
                        passwordsMatch: signUpData.password === signUpData.confirmPassword,
                        servicesSelected: signUpData.services.length > 0,
                        services: signUpData.services
                      });
                    }}
                  >
                    {isLoading ? 'Creating Account...' : 'Start Your Business'}
                  </Button>
                  
                  <div className="text-center text-sm text-gray-600">
                    By signing up, you agree to our Terms of Service and Privacy Policy
                  </div>
                </form>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ProviderAuth;