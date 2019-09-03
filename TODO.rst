=========
Heis TODO
=========

Heis needs to interact with Salt on  number of levels. The question that pops up is
is we want to make pop-enabled interfaces for these systems, it would make a l;ot of
sense to make pop-enavbled interfaces to these:

Obvious:
  Rosters
  ssh wrapper funcs

Questions:
  Returners
  File System Backends
  outputters
  Renderers
  Pillar

The obvious ones would live in heis, but the not obvious ones pose a question. Would it make sense
to bootstrap them as standalone and then validate them via heis and then add them to Salt
along with pop in Magnesium? Or should we just install Salt and call it directly?

Option 1
========

Call Salt Directly, then over time we pull them out into standalone pop projects

Option 2
========

Make Standalone POP projects NOW and adopt a policy of not importing Salt at all
into heis

Option 3
========

Call Salt Directly without the intention of moving away

Option 4
========

Create a standalone pop project that deps Salt, this project then makes a standalone
interface to all of the Salt plugin systems as they are needed in a standard way. Then
we can merge that app into heis.

Over time as we abstract away each Salt interface we can make merge the new apps
into the salt bridge app as a stop-gap. This can also be used as the spine of
adding pop into Salt itself.

Option 5
========

Stub out the interfaces with minimal hooks. The main goal is to get the whole
system working. Then we can come back and retrofit the stubbed out interfaces
one at a time with pop-erized interfaces

Decision
========

I am going with option 5 for now to try and get this bootstrapped, I think that
will likely be the easiest moving forward

Layers
======

This is proving to be tricky:

We need to be able to establish multiple concurrent connections, BUT
these connections need to be re-usable by multiple interfaces...

So lets say that we start up 40 connections. Connection 7 then needs to run
a part of it's job on connection 15. Connection 7 should not need to create a
new connection but use the existing one.

So we should make a target, assign it to the type/user/ip addr to use for
the target and then allow connections to be linked to based on the given
trifecta. This also allows for a connection to be established with
static paramaters and then re-used with minimal paramaters.

This also means that the function wrapper layer can easily use existing
connections or create new ones on the fly.

When a "connection" is used we create a coroutine to encapsulate the request.

Connection clean up is a question. For ssh shell out connections it is not
a big deal, as each heis conenction will create a new ssh shell out connection,
but in the future we will be able to have other forms of connections that
can be long lasting. We would need to determine at what point a connection would
be reaped and closed. I would suggest that we have a cleanup coroutine that
detects when connections are complete and looks for specific functions in
the plugin to close the given connection
