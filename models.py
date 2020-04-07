class Hospital(object):
    
    def __init__(self, name, address, city, num_beds, occupancy):
        self.name = name
        self.address = address
        self.city = city
        self.num_beds = num_beds
        self.occupancy = occupancy
    
    @staticmethod
    def from_dict(source):
        return Hospital(source['name'], source['address'], source['city'], source['num_beds'], source['occupancy'])

    def to_dict(self):
        return {
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'num_beds': self.num_beds,
            'occupancy': self.occupancy
        }
    
    def __repr__(self):
        return 'Hospital(name={}, address={}, city={}, num_beds={}, occupancy={})'.format(self.name, self.address, self.city, self.num_beds, self.occupancy)