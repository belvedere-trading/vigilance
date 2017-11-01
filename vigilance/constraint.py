"""@ingroup vigilance
@file
Contains definitions of code coverage constraints.
"""
import re
from abc import ABCMeta, abstractmethod

from vigilance.representation import Satisfaction

class Constraint(object):
    """Represents a coverage constraint that must be enforced.
    """
    __metaclass__ = ABCMeta

    def is_of_type(self, constraintType):
        """Returns whether the Constraint is considered to be of a certain constraint type.
        """
        return type(self) == constraintType

    @abstractmethod
    def satisfied_by(self, item):
        """Returns whether the Constraint is satisfied by some item under coverage.
        @param item A vigilance.representation.QualityItem instance.
        @returns A vigilance.representation.Satisfaction instance.
        """
        pass

    def applies_to(self, item): #pylint: disable=unused-argument,no-self-use
        """Returns whether the Constraint should be applied to an item under coverage.
        This is useful for allowing specific constraints to be applied to smaller subsets of a codebase.
        @returns A boolean.
        """
        return True

class PackageConstraint(Constraint):
    """A Constraint decorator that applies a Constraint to a specific package only.
    """
    def __init__(self, constraint, packageName):
        self.constraint = constraint
        self.packageName = packageName.lower()

    def is_of_type(self, constraintType):
        return type(self.constraint) == constraintType

    def satisfied_by(self, item):
        return self.constraint.satisfied_by(item)

    def applies_to(self, item):
        return hasattr(item, 'name') and item.name.lower() == self.packageName

class FileConstraint(Constraint):
    """A Constraint decorator that applies a Constraint to specific files only.
    """
    def __init__(self, constraint, pathRegex):
        self.constraint = constraint
        self.pathRegex = pathRegex

    def is_of_type(self, constraintType):
        return type(self.constraint) == constraintType

    def satisfied_by(self, item):
        return self.constraint.satisfied_by(item)

    def applies_to(self, item):
        return hasattr(item, 'filePath') and re.search(self.pathRegex, item.filePath) is not None

class IgnoreFiles(Constraint):
    """A Constraint that causes specified files to be ignored from vigilance entirely.
    """
    def __init__(self, paths):
        self.paths = paths

    def is_of_type(self, _):
        return True

    def satisfied_by(self, _):
        return Satisfaction(True)

    def applies_to(self, item):
        return hasattr(item, 'filePath') and item.filePath in self.paths

class ConstraintSuite(object):
    """Relates multiple constraints together into a constraint suite.
    """
    def __init__(self, constraints):
        self.constraints = constraints

    def all_types(self):
        """Returns an iterable of all available constraint types.
        """
        return self.constraints.itervalues()

    def all_labels(self):
        """Returns an iterable of all available constraint labels.
        """
        return self.constraints.iterkeys()

    def get_constraint(self, label):
        """Returns the constraint associated with a given label.
        @param label The string type representing the constraint.
        @returns A subclass of Constraint.
        """
        return self.constraints[label]

    def group_constraints(self, constraints):
        """Groups constraints into subgroups based on their constraint types.
        @param constraints A list of Constraint instances.
        @returns A dictionary mapping constraint types to distinct subsets of @p constraints.
        """
        return {constraintType: [constraint for constraint in constraints if constraint.is_of_type(constraintType)]
                for constraintType in self.all_types()}

class ConstraintSet(object):
    """Determines which constraints apply to each item under test.
    This "override" functionality allows specific projects/files within a codebase to be given
    different constraints than the global default constraints.
    """
    def __init__(self, constraintSuite, globalConstraints, filteredConstraints):
        self.constraintSuite = constraintSuite
        self.globalConstraints = self.constraintSuite.group_constraints(globalConstraints)
        self.filteredConstraints = self.constraintSuite.group_constraints(filteredConstraints)

    def constraints_for(self, item):
        """Retrieves all constraints that should be considered for a single item under test.
        @param item A vigilance.representation.QualityItem instance.
        @returns A list of Constraint instances.
        """
        constraints = []
        for ctype in self.constraintSuite.all_types():
            constraints.extend([c for c in self.filteredConstraints[ctype] if c.applies_to(item)] or self.globalConstraints[ctype])
        return constraints
