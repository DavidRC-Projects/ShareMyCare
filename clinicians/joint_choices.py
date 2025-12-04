"""
Joint-specific ROM and strength choices for physiotherapy assessments
Based on clinical ROM standards
"""

# Strength/Power Choices - Medical Research Council (MRC) Scale
STRENGTH_CHOICES = [
    ('', 'Select strength...'),
    ('5/5', '5/5 - Normal'),
    ('4/5', '4/5 - Good'),
    ('3/5', '3/5 - Fair'),
    ('2/5', '2/5 - Poor'),
    ('1/5', '1/5 - Trace'),
    ('0/5', '0/5 - None'),
]

# ANKLE ROM CHOICES
ANKLE_DORSIFLEXION_CHOICES = [
    ('', 'Select ROM...'),
    ('20', '20° - Normal'),
    ('15', '15°'),
    ('10', '10°'),
    ('5', '5°'),
    ('0', '0°'),
]

ANKLE_PLANTARFLEXION_CHOICES = [
    ('', 'Select ROM...'),
    ('50', '50° - Normal'),
    ('45', '45°'),
    ('40', '40°'),
    ('30', '30°'),
    ('20', '20°'),
    ('10', '10°'),
]

ANKLE_INVERSION_CHOICES = [
    ('', 'Select ROM...'),
    ('35', '35° - Normal'),
    ('30', '30°'),
    ('25', '25°'),
    ('20', '20°'),
    ('15', '15°'),
    ('10', '10°'),
    ('5', '5°'),
]

ANKLE_EVERSION_CHOICES = [
    ('', 'Select ROM...'),
    ('15', '15° - Normal'),
    ('10', '10°'),
    ('5', '5°'),
    ('0', '0°'),
]

# KNEE ROM CHOICES
KNEE_FLEXION_CHOICES = [
    ('', 'Select ROM...'),
    ('135', '135° - Normal'),
    ('120', '120°'),
    ('110', '110°'),
    ('90', '90°'),
    ('75', '75°'),
    ('60', '60°'),
    ('45', '45°'),
    ('30', '30°'),
]

KNEE_EXTENSION_CHOICES = [
    ('', 'Select ROM...'),
    ('0', '0° - Normal (Full Extension)'),
    ('-5', '-5° (Hyperextension)'),
    ('-10', '-10° (Hyperextension)'),
    ('5', '5° (Flexion Contracture)'),
    ('10', '10° (Flexion Contracture)'),
    ('15', '15° (Flexion Contracture)'),
    ('20', '20° (Flexion Contracture)'),
]

# HIP ROM CHOICES
HIP_FLEXION_CHOICES = [
    ('', 'Select ROM...'),
    ('120', '120° - Normal'),
    ('110', '110°'),
    ('100', '100°'),
    ('90', '90°'),
    ('75', '75°'),
    ('60', '60°'),
    ('45', '45°'),
]

HIP_EXTENSION_CHOICES = [
    ('', 'Select ROM...'),
    ('30', '30° - Normal'),
    ('25', '25°'),
    ('20', '20°'),
    ('15', '15°'),
    ('10', '10°'),
    ('5', '5°'),
    ('0', '0°'),
]

HIP_ABDUCTION_CHOICES = [
    ('', 'Select ROM...'),
    ('45', '45° - Normal'),
    ('40', '40°'),
    ('35', '35°'),
    ('30', '30°'),
    ('25', '25°'),
    ('20', '20°'),
    ('15', '15°'),
]

HIP_ADDUCTION_CHOICES = [
    ('', 'Select ROM...'),
    ('30', '30° - Normal'),
    ('25', '25°'),
    ('20', '20°'),
    ('15', '15°'),
    ('10', '10°'),
    ('5', '5°'),
]

HIP_INTERNAL_ROTATION_CHOICES = [
    ('', 'Select ROM...'),
    ('45', '45° - Normal'),
    ('40', '40°'),
    ('35', '35°'),
    ('30', '30°'),
    ('25', '25°'),
    ('20', '20°'),
    ('15', '15°'),
]

HIP_EXTERNAL_ROTATION_CHOICES = [
    ('', 'Select ROM...'),
    ('45', '45° - Normal'),
    ('40', '40°'),
    ('35', '35°'),
    ('30', '30°'),
    ('25', '25°'),
    ('20', '20°'),
    ('15', '15°'),
]

# LOWER BACK (LUMBAR SPINE) ROM CHOICES
LUMBAR_FLEXION_CHOICES = [
    ('', 'Select ROM...'),
    ('60', '60° - Normal'),
    ('50', '50°'),
    ('40', '40°'),
    ('30', '30°'),
    ('20', '20°'),
    ('10', '10°'),
]

LUMBAR_EXTENSION_CHOICES = [
    ('', 'Select ROM...'),
    ('25', '25° - Normal'),
    ('20', '20°'),
    ('15', '15°'),
    ('10', '10°'),
    ('5', '5°'),
]

LUMBAR_LATERAL_FLEXION_CHOICES = [
    ('', 'Select ROM...'),
    ('25', '25° - Normal'),
    ('20', '20°'),
    ('15', '15°'),
    ('10', '10°'),
    ('5', '5°'),
]

LUMBAR_ROTATION_CHOICES = [
    ('', 'Select ROM...'),
    ('30', '30° - Normal'),
    ('25', '25°'),
    ('20', '20°'),
    ('15', '15°'),
    ('10', '10°'),
    ('5', '5°'),
]

# NECK (CERVICAL SPINE) ROM CHOICES
CERVICAL_FLEXION_CHOICES = [
    ('', 'Select ROM...'),
    ('45', '45° - Normal'),
    ('40', '40°'),
    ('35', '35°'),
    ('30', '30°'),
    ('25', '25°'),
    ('20', '20°'),
    ('15', '15°'),
]

CERVICAL_EXTENSION_CHOICES = [
    ('', 'Select ROM...'),
    ('70', '70° - Normal'),
    ('60', '60°'),
    ('50', '50°'),
    ('40', '40°'),
    ('30', '30°'),
    ('20', '20°'),
]

CERVICAL_LATERAL_FLEXION_CHOICES = [
    ('', 'Select ROM...'),
    ('45', '45° - Normal'),
    ('40', '40°'),
    ('35', '35°'),
    ('30', '30°'),
    ('25', '25°'),
    ('20', '20°'),
    ('15', '15°'),
]

CERVICAL_ROTATION_CHOICES = [
    ('', 'Select ROM...'),
    ('80', '80° - Normal'),
    ('70', '70°'),
    ('60', '60°'),
    ('50', '50°'),
    ('40', '40°'),
    ('30', '30°'),
]

# SHOULDER ROM CHOICES
SHOULDER_FLEXION_CHOICES = [
    ('', 'Select ROM...'),
    ('180', '180° - Normal'),
    ('170', '170°'),
    ('160', '160°'),
    ('150', '150°'),
    ('140', '140°'),
    ('130', '130°'),
    ('120', '120°'),
    ('110', '110°'),
    ('100', '100°'),
    ('90', '90°'),
    ('75', '75°'),
    ('60', '60°'),
]

SHOULDER_EXTENSION_CHOICES = [
    ('', 'Select ROM...'),
    ('60', '60° - Normal'),
    ('50', '50°'),
    ('40', '40°'),
    ('30', '30°'),
    ('20', '20°'),
    ('10', '10°'),
]

SHOULDER_ABDUCTION_CHOICES = [
    ('', 'Select ROM...'),
    ('180', '180° - Normal'),
    ('170', '170°'),
    ('160', '160°'),
    ('150', '150°'),
    ('140', '140°'),
    ('130', '130°'),
    ('120', '120°'),
    ('110', '110°'),
    ('100', '100°'),
    ('90', '90°'),
    ('75', '75°'),
    ('60', '60°'),
]

SHOULDER_INTERNAL_ROTATION_CHOICES = [
    ('', 'Select ROM...'),
    ('70', '70° - Normal'),
    ('60', '60°'),
    ('50', '50°'),
    ('40', '40°'),
    ('30', '30°'),
    ('20', '20°'),
]

SHOULDER_EXTERNAL_ROTATION_CHOICES = [
    ('', 'Select ROM...'),
    ('90', '90° - Normal'),
    ('80', '80°'),
    ('70', '70°'),
    ('60', '60°'),
    ('50', '50°'),
    ('40', '40°'),
    ('30', '30°'),
]

# ELBOW ROM CHOICES
ELBOW_FLEXION_CHOICES = [
    ('', 'Select ROM...'),
    ('150', '150° - Normal'),
    ('140', '140°'),
    ('130', '130°'),
    ('120', '120°'),
    ('110', '110°'),
    ('100', '100°'),
    ('90', '90°'),
    ('75', '75°'),
]

ELBOW_EXTENSION_CHOICES = [
    ('', 'Select ROM...'),
    ('0', '0° - Normal (Full Extension)'),
    ('-5', '-5° (Hyperextension)'),
    ('-10', '-10° (Hyperextension)'),
    ('5', '5° (Flexion Contracture)'),
    ('10', '10° (Flexion Contracture)'),
    ('15', '15° (Flexion Contracture)'),
]

# WRIST ROM CHOICES
WRIST_FLEXION_CHOICES = [
    ('', 'Select ROM...'),
    ('80', '80° - Normal'),
    ('70', '70°'),
    ('60', '60°'),
    ('50', '50°'),
    ('40', '40°'),
    ('30', '30°'),
    ('20', '20°'),
]

WRIST_EXTENSION_CHOICES = [
    ('', 'Select ROM...'),
    ('70', '70° - Normal'),
    ('60', '60°'),
    ('50', '50°'),
    ('40', '40°'),
    ('30', '30°'),
    ('20', '20°'),
    ('10', '10°'),
]

WRIST_RADIAL_DEVIATION_CHOICES = [
    ('', 'Select ROM...'),
    ('20', '20° - Normal'),
    ('15', '15°'),
    ('10', '10°'),
    ('5', '5°'),
]

WRIST_ULNAR_DEVIATION_CHOICES = [
    ('', 'Select ROM...'),
    ('30', '30° - Normal'),
    ('25', '25°'),
    ('20', '20°'),
    ('15', '15°'),
    ('10', '10°'),
    ('5', '5°'),
]

# ROM Choices - Keep for backward compatibility
ROM_CHOICES = [
    ('normal', 'Normal'),
    ('limited', 'Limited (specify in notes)'),
    ('not_assessed', 'Not Assessed'),
]

ROM_CHOICES_WITH_FREE = ROM_CHOICES + [('free_text', 'Free Text')]
KNEE_FLEXION_CHOICES_WITH_FREE = KNEE_FLEXION_CHOICES + [('free_text', 'Free Text')]
HIP_FLEXION_CHOICES_WITH_FREE = HIP_FLEXION_CHOICES + [('free_text', 'Free Text')]
SHOULDER_FLEXION_CHOICES_WITH_FREE = SHOULDER_FLEXION_CHOICES + [('free_text', 'Free Text')]

# Movement choices for each joint
SHOULDER_MOVEMENTS = [
    ('flexion', 'Flexion'),
    ('extension', 'Extension'),
    ('abduction', 'Abduction'),
    ('internal_rotation', 'Internal Rotation'),
    ('external_rotation', 'External Rotation'),
]

ELBOW_MOVEMENTS = [
    ('flexion', 'Flexion'),
    ('extension', 'Extension'),
]

HIP_MOVEMENTS = [
    ('flexion', 'Flexion'),
    ('extension', 'Extension'),
    ('abduction', 'Abduction'),
    ('adduction', 'Adduction'),
    ('internal_rotation', 'Internal Rotation'),
    ('external_rotation', 'External Rotation'),
]

KNEE_MOVEMENTS = [
    ('flexion', 'Flexion'),
    ('extension', 'Extension'),
]

ANKLE_MOVEMENTS = [
    ('dorsiflexion', 'Dorsiflexion'),
    ('plantarflexion', 'Plantarflexion'),
    ('inversion', 'Inversion'),
    ('eversion', 'Eversion'),
]

WRIST_MOVEMENTS = [
    ('flexion', 'Flexion'),
    ('extension', 'Extension'),
    ('radial_deviation', 'Radial Deviation'),
    ('ulnar_deviation', 'Ulnar Deviation'),
]

CERVICAL_MOVEMENTS = [
    ('flexion', 'Flexion'),
    ('extension', 'Extension'),
    ('lateral_flexion_right', 'Lateral Flexion Right'),
    ('lateral_flexion_left', 'Lateral Flexion Left'),
    ('rotation_right', 'Rotation Right'),
    ('rotation_left', 'Rotation Left'),
]

LUMBAR_MOVEMENTS = [
    ('flexion', 'Flexion'),
    ('extension', 'Extension'),
    ('lateral_flexion_right', 'Lateral Flexion Right'),
    ('lateral_flexion_left', 'Lateral Flexion Left'),
    ('rotation_right', 'Rotation Right'),
    ('rotation_left', 'Rotation Left'),
]

# Joint-specific measurement fields (kept for backward compatibility)
JOINT_MEASUREMENTS = {}
