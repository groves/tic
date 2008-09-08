package bootstrap.liftweb

import net.liftweb.util._
import net.liftweb.http._
import net.liftweb.sitemap._
import net.liftweb.sitemap.Loc._
import Helpers._
import java.sql.{Connection, DriverManager}
import sevorg.tic.model._
 
/**
  * A class that's instantiated early and run.  It allows the application to modify lift's
  * environment.
  */
class Boot {
  def boot {
    // where to search snippet
    LiftRules.addToPackages("sevorg.tic")     

    // Set up a LoanWrapper to automatically instantiate and tear down the EntityManager on a
    // per-request basis
    S.addAround(List(new LoanWrapper {
        def apply[T] (f : => T): T = {
            val em = Model.factory.createEntityManager();
            
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
