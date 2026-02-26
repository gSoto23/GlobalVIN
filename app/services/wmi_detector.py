def get_vehicle_origin_from_vin(vin: str) -> str:
    """
    Identifies if a vehicle is from US or South Korea based on the World Manufacturer Identifier (WMI).
    WMI is the first 3 characters of the VIN.
    """
    if not vin or len(vin) < 3:
        return "Unknown"
        
    wmi = vin[0:3].upper()
    first_char = wmi[0]
    first_two_chars = wmi[0:2]
    
    # 1, 4, 5 are United States
    # 2 is Canada, 3 is Mexico - Often batched into US history reports as North America
    if first_char in ('1', '4', '5'):
        return "United States"
        
    # K is for Korea (e.g. KMH Hyundai, KNA Kia)
    if first_char == 'K':
        if first_two_chars in ('KA', 'KB', 'KC', 'KD', 'KE', 'KF', 'KG', 'KH', 'KJ', 'KK', 'KL', 'KM', 'KN', 'KP', 'KR'):
            return "South Korea"
            
    # J is Japan, W is Germany, etc...
    return "Other"
