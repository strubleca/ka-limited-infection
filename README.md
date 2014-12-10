# Project: Limited Infection

Rolling out features on a live web site with active users
requires care to avoid exposing the entire user base
to bad bugs. Features are rolled out slowly, first to a small
subset of users, then to larger and larger sets of users
as bugs are ironed out and the new features are deemed desirable
and robust.

In this particular instance of the feature roll out problem,
we are asked to consider a classroom setting. Ideally,
the entire class is introduced to a feature simultaneously
to avoid confusion between members of the classroom,
students and teachers both, that might see different feature
sets otherwise.

## Running the Implementations


## User Model

The original problem description states:

> We can use the heuristic that each teacher­student pair should
be on the same version of the site. So if A coaches B and we want
to give A a new feature, then B should also get the new feature.
Note that infections are transitive ­ if B coaches C, then C should
get the new feature as well. Also, infections are transferred by
both the "coaches" and "is coached by" relations.

Because infections are transferred by "coaches" and "is coached by"
relations, an **undirected graph** is used to model the complete
set of relationships. For example, if a student is chosen for initial
infection, their teacher(s) will be infected in the same way that
initially infecting a teacher will infect their student(s).

It is important to note that in general, undirected graphs might
consist of several **connected components**. It is possible that
a component consists of a single, lonely student or teacher.
Alternatively, everyone could be connected, by some path of
coaching relationships, to everyone else.

An individual user is modeled as a list of web site features
that they currently have, which defines the version of the site
they see. In a very controlled setting, a more limited number
of feature combinations might be allowed and defined by a simple
identifier. To keep the code simple, features are implemented as
strings.

```python
class User:
    """A user of the system"""
    def __init__(self):
        """Construct and initialize a user of the web site."""
        self.features = []
        self.coaches = []
        self.coached_by = []
```

## Total Infection

The original problem statement states:

> Starting from any given user, the entire connected component of
the coaching graph containing that user should become infected.

```python
def total_infection(initial_user, feature):
    """Infect the connected component containing the initial_user with
       the specified feature.
    """
```

## Limited Infection

Total infection provides limited control over the proportion
of the coaching graph that will be infected. A second part
of the original problem states:

> We would like to be able to infect close to a given number of
users. Ideally we’d like a coach and all of their students to either
have a feature or not. However, that might not always be possible.

```python
def limited_infection(graph, feature, num_users, tolerance):
    """Infect close to a given number of users in the coaching graph."""
```
