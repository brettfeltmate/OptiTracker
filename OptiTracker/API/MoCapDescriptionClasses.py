# TODO: document

from construct import Struct
from .MoCapDescriptionStructures import MOCAP_DESCRIPTION_STRUCTS

class DescriptionAsset:
    def __init__(self, motive_version, bytestream = None) -> None:
        self.motive_version = motive_version  # Determines which structure to use
        self._structure = self._structure()   # Asset specific Construct Struct
        self._parsed = None                   # To store parsed description

        # Parse data if provided during instantiation
        if bytestream is not None:
            self.parse(bytestream)

    # Fetches child-appropriate description Struct(), conditioned on motive version
    def _structure(self) -> Struct:
        struct_dict = MOCAP_DESCRIPTION_STRUCTS[type(self)]
        return struct_dict.get(self.motive_version, struct_dict['default'])
    
    # TODO: Determining expected offset a priori might be handy; not sure how to do this
    # Returns landing position in datastream after parsing
    def offset(self) -> int:
        # NOTE: Offset pruned out when dump()ing data 
        if self._parsed is not None:
            return self._parsed['offset']
        
    # Shadows Construct.Struct.parse() method
    def parse(self, bytestream) -> None:
        self._parsed = self._structure.parse(bytestream)

    # Coerces description parcels into list[dict]; bundling procedure varies by child
    #       NOTE: Children drop terminal entries (1 = obj addr, -1 = offset)
    def dump(self) -> list[dict]:
        raise NotImplementedError("AssetDescriptionStruct.dump() | Must be implemented by child class.")
    
#
# DescriptionAsset Child classes
#
    
# Parses frame number; seems overkill
class DescriptionPrefix(DescriptionAsset):
    def __init__(self, motive_version, bytestream = None) -> None:
        super().__init__(motive_version, bytestream)     
        
    def dump(self) -> list[dict]:
        return [dict(list(self._parsed.items())[1:-1])]
    

# Parses N-i MarkerSets, each composed of N-j Markers
class DescriptionMarkerSets(DescriptionAsset):
    def __init__(self, motive_version, bytestream = None) -> None:
        super().__init__(motive_version, bytestream)

    def dump(self) -> list[dict]:
        return [dict(list(marker.items())[1:]) 
                for marker_set in self._parsed.marker_sets
                for marker in marker_set.markers]
    

# Parses N-i RigidBodies NOT integral to skeletons, each composed of N-j RigidBody(s)
class DescriptionRigidBodies(DescriptionAsset):
    def __init__(self, motive_version, bytestream = None) -> None:
        super().__init__(motive_version, bytestream)

    def dump(self) -> list[dict]:
        return [dict(list(rb.items())[1:]) 
                for rb in self._parsed.rigid_bodies]
    
# Parses N-i Skeletons, each composed of N-j RigidBodies, each composed of N-k RigidBody(s)
class DescriptionSkeletons(DescriptionAsset):
    def __init__(self, motive_version, bytestream = None) -> None:
        super().__init__(motive_version, bytestream)

    def dump(self) -> list[dict]:
        return [dict(list(rb.items())[1:]) 
                for skeleton in self._parsed.skeletons
                for rb_set in skeleton.rigid_body_sets
                for rb in rb_set.rigid_bodies]
    

# NOTE: JFC labeled markers ARE just regular markers...
# Parses N-i LabeledMarkers, each composed of N-j Marker(s)
# class DescriptionLabeledMarkers(DescriptionAsset):
#     def __init__(self, motive_version, bytestream = None) -> None:
#         super().__init__(motive_version, bytestream)

#     def dump(self) -> list[dict]:
#         return [dict(list(marker.items())[1:]) 
#                 for marker in self._parsed.labeled_markers]
    
# Parses N-i ForcePlates, each plate composed of N-j Channel(s)
class DescriptionForcePlates(DescriptionAsset):
    def __init__(self, motive_version, bytestream = None) -> None:
        super().__init__(motive_version, bytestream)

    def dump(self) -> list[dict]:
        # TODO: Figuring out tidy way of returning matrices is Future Brett's problem
        pass
        return [dict(list(channel.items())[1:]) 
                for plate in self._parsed.force_plates
                for channel in plate.channels]
    

# Parses N-i Devices, each device composed of N-j Channel(s)
class DescriptionDevices(DescriptionAsset):
    def __init__(self, motive_version, bytestream = None) -> None:
        super().__init__(motive_version, bytestream)

    def dump(self) -> list[dict]:
        return [dict(list(channel.items())[1:]) 
                for device in self._parsed.devices
                for channel in device.channels]
    

class DescriptionCameras(DescriptionAsset):
    def __init__(self, motive_version, bytestream = None) -> None:
        super().__init__(motive_version, bytestream)

    def dump(self) -> list[dict]:
        return [dict(list(camera.items())[1:]) 
                for camera in self._parsed.cameras]
    