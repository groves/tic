package bootstrap.liftweb

import javax.persistence.Persistence

import net.liftweb.util._
import net.liftweb.http._
import Helpers._
import sevorg.tic.model._
 
/**
  * A class that's instantiated early and run.  It allows the application to modify lift's environment.
  */
class Boot {
  def boot {
    // where to search snippet
    LiftRules.addToPackages("sevorg.tic")     

    // Create the EntityManagerFactory for this instance and kill it when the servlet shuts down
    val factory = Persistence.createEntityManagerFactory("tic");
    LiftRules.addUnloadHook(() => {factory.close});

    // Set up a LoanWrapper to automatically instantiate and tear down the EntityManager on a per-request basis
    S.addAround(List(new LoanWrapper {
        def apply[T] (f : => T): T = {
            val em = factory.createEntityManager();
            
            // Add EM into S scope
            Model.emVar.set(em)
	  
            try {
              f
            } finally {
              em.close()
            }
        }
      }));
  }
}
